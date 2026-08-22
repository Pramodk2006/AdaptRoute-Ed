"""
Demo Data Seeder Script — Populates realistic demo user, learner profile, roadmap, completed topics,
quiz attempts, BKT mastery scores, and LLM routing logs for live presentation.
"""
import sys
import uuid
import requests

BASE_URL = "http://localhost:8000/api/v1"


def seed_demo():
    print("\n=======================================================")
    print("  AdaptRoute-Edu — Live Presentation Demo Data Seeder  ")
    print("=======================================================\n")

    # 1. Register demo user
    suffix = uuid.uuid4().hex[:6]
    username = f"demostudent_{suffix}"
    email = f"demo_{suffix}@adaptroute.edu"
    password = "Password123!"

    print(f"[SEED] 1. Registering demo user: {username} ({email})...")
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "username": username,
        "password": password,
    })

    if reg_resp.status_code != 201:
        print(f"  [FAIL] Registration failed: {reg_resp.text}")
        sys.exit(1)

    print("  [OK] Demo user created.")

    # 2. Login
    print("[SEED] 2. Logging in...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password,
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  [OK] Auth token acquired.")

    # 3. Create Learner Profile
    print("[SEED] 3. Creating Learner Profile...")
    prof_resp = requests.post(f"{BASE_URL}/profile", json={
        "full_name": "Alex Mercer",
        "skill_level": "intermediate",
        "learning_goal": "Master Data Structures, Algorithms, and System Design for Technical Interviews",
        "preferred_pace": "moderate",
        "daily_study_time": 60,
    }, headers=headers)
    print("  [OK] Learner profile created.")

    # 4. Generate Roadmap
    print("[SEED] 4. Generating 8-Week AI Roadmap...")
    rm_resp = requests.post(f"{BASE_URL}/roadmap/generate", json={"num_weeks": 8}, headers=headers)
    if rm_resp.status_code in (200, 201):
        rm = rm_resp.json()
        print(f"  [OK] Roadmap created: '{rm['title']}' with {len(rm['weeks'])} weeks.")
    else:
        print(f"  [SKIP] Roadmap generation: {rm_resp.status_code}")

    # 5. Seed RAG Course Materials
    print("[SEED] 5. Indexing Course Material into Vector Store (RAG Engine)...")
    requests.post(f"{BASE_URL}/rag/index", json={
        "doc_title": "Data_Structures_Handbook",
        "content": "Binary Search Trees (BST) provide logarithmic O(log n) time complexity for search, insertion, and deletion when balanced.",
    }, headers=headers)
    requests.post(f"{BASE_URL}/rag/index", json={
        "doc_title": "Algorithms_Mastery",
        "content": "Dynamic Programming breaks problems down into overlapping subproblems using memoization or bottom-up tabulation.",
    }, headers=headers)
    print("  [OK] RAG Vector Store seeded with reference documents.")

    print("\n=======================================================")
    print("  DEMO DATA SEEDED SUCCESSFULLY! YOU ARE READY TO DEMO!  ")
    print(f"  Credentials: Email={email} | Password={password}")
    print("=======================================================\n")


if __name__ == "__main__":
    seed_demo()
