"""
RoadmapService — orchestrates LLM + DB for roadmap and content generation.
"""
import asyncio
import json
from collections import defaultdict
from uuid import UUID

from fastapi import HTTPException, status

from app.llm.factory import get_provider
from app.models.user import User
from app.prompts.content_prompt import build_content_prompt
from app.prompts.roadmap_prompt import build_roadmap_prompt
from app.repositories.profile_repository import ProfileRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.services.curriculum_generator import generate_tailored_curriculum
from app.services.study_content_generator import generate_tailored_study_content
from app.schemas.roadmap import (
    GenerateRoadmapRequest,
    RoadmapResponse,
    TopicContentResponse,
    TopicResponse,
    WeekGroup,
    ContentResponse,
)
from app.utils.logger import logger


class RoadmapService:
    def __init__(
        self,
        roadmap_repo: RoadmapRepository,
        profile_repo: ProfileRepository,
    ) -> None:
        self.roadmap_repo = roadmap_repo
        self.profile_repo = profile_repo

    # ── Generate Roadmap ────────────────────────────────────────
    async def generate_roadmap(
        self, user: User, payload: GenerateRoadmapRequest
    ) -> RoadmapResponse:
        profile = self.profile_repo.get_by_user_id(user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Complete your learner profile before generating a roadmap.",
            )

        # Build prompt and call LLM
        prompt = build_roadmap_prompt(
            learning_goal=profile.learning_goal,
            skill_level=profile.skill_level,
            preferred_pace=profile.preferred_pace,
            daily_study_time_minutes=profile.daily_study_time,
            num_weeks=payload.num_weeks,
        )

        from app.services.adaptive_llm_service import AdaptiveLLMService
        response = await AdaptiveLLMService.generate(
            db_session=self.roadmap_repo.db,
            user_id=user.id,
            task_type="roadmap",
            prompt=prompt,
            user_skill_level=profile.skill_level,
            preferred_pace=profile.preferred_pace,
            daily_study_time=profile.daily_study_time,
            is_json=True,
        )
        raw = response.text
        data = self._parse_llm_json(raw, context="roadmap")

        # Deactivate any previous active roadmaps for this user
        self.roadmap_repo.deactivate_old_roadmaps(user.id)

        # Persist roadmap
        roadmap = self.roadmap_repo.create_roadmap(
            user_id=user.id,
            title=data.get("title", f"Learning Roadmap: {profile.learning_goal[:50]}"),
            goal=data.get("goal", profile.learning_goal),
            total_weeks=payload.num_weeks,
            llm_model=response.model,
        )

        # Flexible topic extraction across LLM response variants
        topics_data = []
        weeks_list = data.get("weeks") or data.get("schedule") or data.get("modules") or data.get("curriculum") or []

        if isinstance(weeks_list, list) and len(weeks_list) > 0:
            for idx, week in enumerate(weeks_list, start=1):
                week_num = week.get("week_number") or week.get("week") or idx
                raw_topics = week.get("topics") or week.get("items") or week.get("lessons") or []
                if isinstance(raw_topics, list):
                    for t_idx, topic in enumerate(raw_topics):
                        if isinstance(topic, str):
                            t_title = topic
                            t_desc = f"Study and practice: {topic}"
                        elif isinstance(topic, dict):
                            t_title = topic.get("title") or topic.get("name") or "Core Concept"
                            t_desc = topic.get("description") or topic.get("summary") or f"Learn {t_title}"
                        else:
                            continue
                        topics_data.append({
                            "roadmap_id": roadmap.id,
                            "week_number": int(week_num),
                            "title": t_title,
                            "description": t_desc,
                            "order_index": t_idx,
                            "is_completed": False,
                        })

        # Intelligent domain-tailored curriculum generator fallback
        if len(topics_data) == 0 or any("Foundation" in t.get("title", "") for t in topics_data):
            tailored_weeks = generate_tailored_curriculum(profile.learning_goal, payload.num_weeks)
            topics_data = []
            for w in tailored_weeks:
                for t in w["topics"]:
                    topics_data.append({
                        "roadmap_id": roadmap.id,
                        "week_number": w["week_number"],
                        "title": t["title"],
                        "description": t["description"],
                        "order_index": t["order_index"],
                        "is_completed": False,
                    })

        topics = self.roadmap_repo.bulk_create_topics(topics_data)

        # Commit everything
        self.roadmap_repo.db.commit()

        # Create initial progress record
        self.roadmap_repo.get_or_create_progress(
            user_id=user.id,
            roadmap_id=roadmap.id,
            total_topics=len(topics),
        )

        logger.info(f"Roadmap created id={roadmap.id} topics={len(topics)}")
        return self._build_roadmap_response(roadmap)

    # ── Get Active Roadmap ──────────────────────────────────────
    def get_roadmap(self, user: User) -> RoadmapResponse:
        roadmap = self.roadmap_repo.get_active_roadmap(user.id)
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active roadmap found. Generate one first.",
            )
        return self._build_roadmap_response(roadmap)

    # ── Mark Topic Complete ─────────────────────────────────────
    def complete_topic(self, user: User, topic_id: UUID) -> TopicResponse:
        topic = self.roadmap_repo.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found.")

        roadmap = self.roadmap_repo.get_roadmap_by_id(topic.roadmap_id, user.id)
        if not roadmap:
            raise HTTPException(status_code=403, detail="Access denied.")

        topic = self.roadmap_repo.mark_topic_complete(topic)
        self.roadmap_repo.update_progress_on_topic_complete(roadmap.id)
        return TopicResponse.model_validate(topic)

    # ── Generate Content ────────────────────────────────────────
    async def generate_content(self, user: User, topic_id: UUID, force: bool = False) -> TopicContentResponse:
        topic = self.roadmap_repo.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found.")

        roadmap = self.roadmap_repo.get_roadmap_by_id(topic.roadmap_id, user.id)
        if not roadmap:
            raise HTTPException(status_code=403, detail="Access denied.")

        existing = self.roadmap_repo.get_content_for_topic(topic_id)
        is_generic_cache = False
        if existing and not force:
            for c in existing:
                body_lower = c.body.lower()
                if (
                    "adaptroute learning system" in body_lower
                    or "key concept overview" in body_lower
                    or "key concept or point" in body_lower
                    or "generic" in body_lower
                    or "step-by-step practical application" in body_lower
                ):
                    is_generic_cache = True
                    break

        if not force:
            if existing and not is_generic_cache:
                return TopicContentResponse(
                    topic=TopicResponse.model_validate(topic),
                    contents=[ContentResponse.model_validate(c) for c in existing],
                )

            # Auto-populate domain-tailored study content on GET (< 10ms)
            data = generate_tailored_study_content(topic.title, topic.description or "", roadmap.goal)
            provider_name = "tailored-curriculum-engine"

            if existing:
                for c in existing:
                    self.roadmap_repo.db.delete(c)
                self.roadmap_repo.db.flush()

            contents_data = []
            notes_body = "\n".join(f"• {n}" for n in data.get("notes", []))
            if notes_body:
                contents_data.append({
                    "topic_id": topic_id,
                    "content_type": "notes",
                    "body": notes_body,
                    "llm_model_used": provider_name,
                })
            if data.get("explanation"):
                contents_data.append({
                    "topic_id": topic_id,
                    "content_type": "explanation",
                    "body": data["explanation"],
                    "llm_model_used": provider_name,
                })
            for ex in data.get("examples", []):
                contents_data.append({
                    "topic_id": topic_id,
                    "content_type": "example",
                    "body": json.dumps(ex) if isinstance(ex, dict) else str(ex),
                    "llm_model_used": provider_name,
                })

            contents = self.roadmap_repo.create_contents(contents_data)
            return TopicContentResponse(
                topic=TopicResponse.model_validate(topic),
                contents=[ContentResponse.model_validate(c) for c in contents],
            )

        # Clear existing cached rows if forced or generic
        if existing and (force or is_generic_cache):
            for c in existing:
                self.roadmap_repo.db.delete(c)
            self.roadmap_repo.db.flush()

        profile = self.profile_repo.get_by_user_id(user.id)
        prompt = build_content_prompt(
            topic_title=topic.title,
            topic_description=topic.description or "",
            skill_level=profile.skill_level if profile else "beginner",
            learning_goal=roadmap.goal,
        )

        from app.services.adaptive_llm_service import AdaptiveLLMService
        try:
            response = await AdaptiveLLMService.generate(
                db_session=self.roadmap_repo.db,
                user_id=user.id,
                task_type="content",
                prompt=prompt,
                user_skill_level=profile.skill_level if profile else "beginner",
                preferred_pace=profile.preferred_pace if profile else "moderate",
                daily_study_time=profile.daily_study_time if profile else 60,
                is_json=True,
            )
            raw = response.text
            data = self._parse_llm_json(raw, context="content")
            provider_name = response.model
        except Exception as e:
            logger.warning(f"LLM content generation warning: {e}, using fallback generator")
            data = generate_tailored_study_content(topic.title, topic.description or "", roadmap.goal)
            provider_name = "tailored-curriculum-engine"

        # Fallback check if LLM JSON missing required keys
        if not data.get("notes") or not data.get("explanation"):
            data = generate_tailored_study_content(topic.title, topic.description or "", roadmap.goal)
            provider_name = "tailored-curriculum-engine"

        contents_data = []
        # Notes
        notes_body = "\n".join(f"• {n}" for n in data.get("notes", []))
        if notes_body:
            contents_data.append({
                "topic_id": topic_id,
                "content_type": "notes",
                "body": notes_body,
                "llm_model_used": provider_name,
            })
        # Explanation
        if data.get("explanation"):
            contents_data.append({
                "topic_id": topic_id,
                "content_type": "explanation",
                "body": data["explanation"],
                "llm_model_used": provider_name,
            })
        # Examples
        for ex in data.get("examples", []):
            contents_data.append({
                "topic_id": topic_id,
                "content_type": "example",
                "body": json.dumps(ex) if isinstance(ex, dict) else str(ex),
                "llm_model_used": provider_name,
            })

        contents = self.roadmap_repo.create_contents(contents_data)
        return TopicContentResponse(
            topic=TopicResponse.model_validate(topic),
            contents=[ContentResponse.model_validate(c) for c in contents],
        )

    async def generate_content_stream(self, user: User, topic_id: UUID):
        """Yield real-time SSE stream of study content tokens for a topic."""
        topic = self.roadmap_repo.get_topic_by_id(topic_id)
        if not topic:
            yield "Topic not found."
            return

        roadmap = self.roadmap_repo.get_roadmap_by_id(topic.roadmap_id)
        if not roadmap or roadmap.user_id != user.id:
            yield "Unauthorized access to topic content."
            return

        profile = self.profile_repo.get_by_user_id(user.id)
        prompt = build_content_prompt(
            topic_title=topic.title,
            topic_description=topic.description or "",
            skill_level=profile.skill_level if profile else "beginner",
            learning_goal=roadmap.goal,
        )

        from app.services.adaptive_llm_service import AdaptiveLLMService
        async for token in AdaptiveLLMService.generate_stream(
            db_session=self.roadmap_repo.db,
            user_id=user.id,
            task_type="content",
            prompt=prompt,
            user_skill_level=profile.skill_level if profile else "beginner",
            preferred_pace=profile.preferred_pace if profile else "moderate",
            daily_study_time=profile.daily_study_time if profile else 60,
            max_tokens=1000,
        ):
            yield token

    # ── Helpers ─────────────────────────────────────────────────
    def _parse_llm_json(self, raw: str, context: str) -> dict:
        """Strip markdown fences and parse JSON from LLM output."""
        text = raw.strip()
        # Strip ```json ... ``` fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning(f"Failed to parse LLM JSON [{context}]: {exc}\nRaw: {raw[:200]}")
            return {}

    def _build_roadmap_response(self, roadmap) -> RoadmapResponse:
        topics = self.roadmap_repo.get_topics_for_roadmap(roadmap.id)
        week_map: dict = defaultdict(list)
        for t in topics:
            week_map[t.week_number].append(TopicResponse.model_validate(t))

        weeks = [
            WeekGroup(week_number=wn, topics=week_map[wn])
            for wn in sorted(week_map.keys())
        ]
        return RoadmapResponse(
            id=roadmap.id,
            user_id=roadmap.user_id,
            title=roadmap.title,
            goal=roadmap.goal,
            total_weeks=roadmap.total_weeks,
            status=roadmap.status,
            llm_model_used=roadmap.llm_model_used,
            created_at=roadmap.created_at,
            weeks=weeks,
        )
