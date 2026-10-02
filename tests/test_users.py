import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.database import Base, get_db
from app.models.user import User

# Test in-memory database with shared connection pool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_user_and_validation():
    # Valid payload
    payload = {
        "name": "Alex Taylor",
        "age": 28,
        "weight": 74.0,
        "goal": "Muscle Gain",
        "intensity": "Medium",
        "experience": "Intermediate",
        "workout_location": "Gym",
        "preferred_days": ["Monday", "Wednesday", "Friday"]
    }
    response = client.post("/api/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alex Taylor"
    assert data["age"] == 28
    assert data["id"] is not None

    # Invalid age validation
    bad_payload = payload.copy()
    bad_payload["age"] = 5
    bad_response = client.post("/api/users", json=bad_payload)
    assert bad_response.status_code == 422


def test_get_user_by_id():
    # Fetch user created in previous test
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

    # Non-existent user
    not_found = client.get("/api/users/9999")
    assert not_found.status_code == 404
