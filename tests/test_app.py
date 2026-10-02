import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.ai.workout_generator import generate_fallback_plan

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup if needed


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_fallback_plan_structure():
    profile = {
        "name": "Saran",
        "age": 20,
        "weight": 70,
        "height": 170,
        "goal": "Weight Loss",
        "intensity": "Medium",
        "experience": "Beginner",
        "location": "Home",
        "equipment": "Dumbbells",
        "preferred_days": ["Monday", "Wednesday", "Friday"]
    }
    plan = generate_fallback_plan(profile)
    assert "days" in plan
    assert len(plan["days"]) == 7
    assert "nutrition" in plan
    assert "protein_guidance" in plan["nutrition"]
    assert "disclaimer" in plan

    day_names = [d["day"] for d in plan["days"]]
    assert day_names == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def test_api_generate_and_feedback_flow():
    # 1. Generate Plan
    payload = {
        "name": "Saran",
        "age": 20,
        "weight": 70.0,
        "height": 170.0,
        "goal": "Weight Loss",
        "intensity": "Medium",
        "experience": "Beginner",
        "location": "Home",
        "equipment": "Dumbbells",
        "preferred_days": ["Monday", "Wednesday", "Friday"]
    }

    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user_id"] is not None
    assert data["plan_id"] is not None
    assert "days" in data["plan"]
    assert len(data["plan"]["days"]) == 7

    user_id = data["user_id"]
    plan_id = data["plan_id"]

    # 2. Get Plan by ID
    plan_resp = client.get(f"/api/plan/{plan_id}")
    assert plan_resp.status_code == 200
    plan_data = plan_resp.json()
    assert plan_data["success"] is True
    assert plan_data["original_plan"] is not None

    # 3. Mark Day Complete
    comp_resp = client.post(f"/api/plan/{plan_id}/complete", json={"day": "Monday", "completed": True})
    assert comp_resp.status_code == 200
    assert "Monday" in comp_resp.json()["completed_days"]

    # 4. Submit Feedback
    fb_resp = client.post("/api/feedback", json={
        "plan_id": plan_id,
        "feedback": "Add more cardio"
    })
    assert fb_resp.status_code == 200
    assert fb_resp.json()["success"] is True

    # 5. Verify History has Version 1 and Version 2
    hist_resp = client.get(f"/api/history/{user_id}")
    assert hist_resp.status_code == 200
    history = hist_resp.json()["history"]
    assert len(history) >= 2
    assert history[0]["version"] == 1
