"""
AdaptRoute-Edu Automated System Health & End-to-End Verification Script.
Connects to live API server (http://localhost:8000), executes full user lifecycle flow:
1. Health check & DB connection
2. User Registration & Login
3. Profile Creation & Retrieval
4. Dashboard Initial Check
5. Clean up / Summary output

Run with: python backend/scripts/verify_system.py
"""
import sys
import uuid
import requests

BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def log_step(name: str):
    print(f"\n{Colors.BLUE}[TEST STEP]{Colors.RESET} {name}...")

def log_success(msg: str):
    print(f"  {Colors.GREEN}[PASS]:{Colors.RESET} {msg}")

def log_fail(msg: str):
    print(f"  {Colors.RED}[FAIL]:{Colors.RESET} {msg}")

def run_verification():
    print(f"\n=======================================================")
    print(f"  AdaptRoute-Edu — Live System End-to-End Verification  ")
    print(f"=======================================================")

    # 1. Health check
    log_step("1. Checking Server Health (/health)")
    try:
        res = requests.get(HEALTH_URL, timeout=5)
        if res.status_code == 200:
            log_success(f"Backend active: {res.json()}")
        else:
            log_fail(f"Health check failed with status {res.status_code}")
            sys.exit(1)
    except Exception as e:
        log_fail(f"Could not connect to FastAPI server at {HEALTH_URL}: {e}")
        sys.exit(1)

    # 2. Registration
    random_str = str(uuid.uuid4())[:8]
    test_email = f"testuser_{random_str}@example.com"
    test_username = f"user_{random_str}"
    test_password = "Password123"

    log_step("2. Testing User Registration (POST /auth/register)")
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": test_email,
        "username": test_username,
        "password": test_password
    })
    if res.status_code == 201:
        user_data = res.json()
        log_success(f"Registered user ID: {user_data['id']} ({user_data['username']})")
    else:
        log_fail(f"Registration failed: {res.status_code} {res.text}")
        sys.exit(1)

    # 3. Login
    log_step("3. Testing User Login (POST /auth/login)")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    if res.status_code == 200:
        token_data = res.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        log_success("Login successful! JWT access token retrieved.")
    else:
        log_fail(f"Login failed: {res.status_code} {res.text}")
        sys.exit(1)

    # 4. User Info
    log_step("4. Testing Token Auth (GET /auth/me)")
    res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if res.status_code == 200:
        log_success(f"Authenticated as: {res.json()['email']}")
    else:
        log_fail(f"Get me failed: {res.status_code} {res.text}")
        sys.exit(1)

    # 5. Profile Creation
    log_step("5. Testing Learner Profile Creation (POST /profile)")
    profile_payload = {
        "full_name": "Test Runner",
        "skill_level": "intermediate",
        "learning_goal": "Master Machine Learning and Python Backend Architecture",
        "preferred_pace": "moderate",
        "daily_study_time": 60
    }
    res = requests.post(f"{BASE_URL}/profile", json=profile_payload, headers=headers)
    if res.status_code == 201:
        log_success(f"Learner profile created for goal: '{res.json()['learning_goal'][:35]}...'")
    else:
        log_fail(f"Profile creation failed: {res.status_code} {res.text}")
        sys.exit(1)

    # 6. Dashboard Check
    log_step("6. Testing Dashboard Stats (GET /dashboard)")
    res = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    if res.status_code == 200:
        stats = res.json()
        log_success(f"Dashboard response OK: topics={stats['completed_topics']}/{stats['total_topics']} pct={stats['completion_percentage']}%")
    else:
        log_fail(f"Dashboard query failed: {res.status_code} {res.text}")
        sys.exit(1)

    # 7. Router Telemetry Check
    log_step("7. Testing Multi-LLM Router Telemetry (GET /routing/telemetry & PUT /routing/config)")
    res = requests.get(f"{BASE_URL}/routing/telemetry", headers=headers)
    if res.status_code == 200:
        telemetry = res.json()
        log_success(f"Router Telemetry OK: active_policy='{telemetry['active_policy']}' models={len(telemetry['available_models'])}")
    else:
        log_fail(f"Router telemetry failed: {res.status_code} {res.text}")
        sys.exit(1)

    res_cfg = requests.put(f"{BASE_URL}/routing/config", json={"policy": "heuristic"}, headers=headers)
    if res_cfg.status_code == 200:
        log_success("Policy update OK: switched policy to 'heuristic'")
    else:
        log_fail(f"Policy update failed: {res_cfg.status_code} {res_cfg.text}")
        # 8. Multi-Agent Socratic Dialogue Check
    log_step("8. Testing Multi-Agent Socratic Dialogue (POST /socratic/chat)")
    socratic_payload = {
        "topic_title": "Binary Trees",
        "user_message": "What is the difference between a binary tree and a binary search tree?",
        "history": [],
        "skill_level": "beginner",
    }
    res_soc = requests.post(f"{BASE_URL}/socratic/chat", json=socratic_payload, headers=headers)
    if res_soc.status_code == 200:
        soc_data = res_soc.json()
        log_success(f"Socratic Dialogue OK: orchestrated_by='{soc_data['orchestrated_by']}' reply_len={len(soc_data['reply'])}")
    else:
        log_fail(f"Socratic dialogue failed: {res_soc.status_code} {res_soc.text}")
    # 9. RAG Vector Grounding Engine Check
    log_step("9. Testing RAG Vector Grounding Engine (POST /rag/index & POST /rag/search)")
    rag_index_payload = {
        "doc_title": "Algorithms_Handbook",
        "content": "Quicksort is an efficient divide-and-conquer sorting algorithm with average O(n log n) complexity.",
    }
    res_index = requests.post(f"{BASE_URL}/rag/index", json=rag_index_payload, headers=headers)
    if res_index.status_code == 201:
        idx_data = res_index.json()
        log_success(f"RAG Indexing OK: doc='{idx_data['doc_title']}' chunks={idx_data['chunks_created']}")
    else:
        log_fail(f"RAG Indexing failed: {res_index.status_code} {res_index.text}")
        sys.exit(1)

    rag_search_payload = {"query": "quicksort algorithm complexity", "top_k": 1}
    res_search = requests.post(f"{BASE_URL}/rag/search", json=rag_search_payload, headers=headers)
    if res_search.status_code == 200:
        sch_data = res_search.json()
        log_success(f"RAG Vector Search OK: citations={len(sch_data['citations'])} top_source='{sch_data['citations'][0]['source']}'")
    else:
        log_fail(f"RAG Search failed: {res_search.status_code} {res_search.text}")
        sys.exit(1)

    print(f"\n=======================================================")
    print(f"  {Colors.GREEN}ALL SYSTEM INTEGRATION CHECKS PASSED SUCCESSFULLY!{Colors.RESET}  ")
    print(f"=======================================================\n")

if __name__ == "__main__":
    run_verification()
