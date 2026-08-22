"""
LinUCB repository — manages persistence of bandit policy matrices (A and b)
in the PostgreSQL database.
"""
import json
from typing import Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session

from app.models.linucb_state import LinUCBState
from app.utils.logger import logger


class LinUCBRepository:
    def __init__(self, db: Session):
        self.db = db

    def load_arm_state(self, model_id: str, feature_dim: int) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Load A matrix and b vector for a model arm from the database.
        Returns Tuple (A, b) if state exists, otherwise None.
        """
        try:
            state = self.db.query(LinUCBState).filter(LinUCBState.model_id == model_id).first()
            if not state:
                return None

            A = np.array(json.loads(state.a_matrix), dtype=float)
            b = np.array(json.loads(state.b_vector), dtype=float).reshape(-1, 1)

            if A.shape != (feature_dim, feature_dim) or b.shape != (feature_dim, 1):
                logger.warning(
                    f"Saved state for model '{model_id}' shape mismatch. "
                    f"Expected A={(feature_dim, feature_dim)}, b={(feature_dim, 1)}. "
                    f"Got A={A.shape}, b={b.shape}. Discarding state."
                )
                return None

            return A, b
        except Exception as e:
            logger.error(f"Failed to load LinUCB state for model '{model_id}': {e}")
            return None

    def save_arm_state(self, model_id: str, A: np.ndarray, b: np.ndarray) -> bool:
        """
        Persist A matrix and b vector for a model arm to the database.
        Returns True if successful, False otherwise.
        """
        try:
            state = self.db.query(LinUCBState).filter(LinUCBState.model_id == model_id).first()
            a_str = json.dumps(A.tolist())
            b_str = json.dumps(b.flatten().tolist())

            if state:
                state.a_matrix = a_str
                state.b_vector = b_str
                state.update_count += 1
            else:
                state = LinUCBState(
                    model_id=model_id,
                    a_matrix=a_str,
                    b_vector=b_str,
                    update_count=1,
                )
                self.db.add(state)

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save LinUCB state for model '{model_id}': {e}")
            return False
