import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.database import Base
from app.models.admin import Admin
from app.models.user import User
from app.services.admin_service import AdminService
from app.utils.security import hash_password

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def test_admin_auth_and_real_stats():
    db = TestingSession()
    # Seed admin
    admin = Admin(username="superadmin", password_hash=hash_password("adminpass"))
    db.add(admin)
    db.commit()

    # Authenticate success
    auth_admin = AdminService.authenticate(db, "superadmin", "adminpass")
    assert auth_admin is not None
    assert auth_admin.username == "superadmin"

    # Authenticate failure
    fail_admin = AdminService.authenticate(db, "superadmin", "wrongpass")
    assert fail_admin is None

    # Test real stats
    stats = AdminService.get_real_stats(db)
    assert stats["total_users"] == 0
    assert stats["plans_generated"] == 0
    assert stats["plans_updated"] == 0
    assert stats["feedback_submitted"] == 0

    # Add user
    user = User(
        name="Test Athlete",
        age=30,
        weight=80.0,
        goal="Muscle Gain",
        intensity="High",
        experience="Intermediate",
        workout_location="Gym",
        preferred_days="[]"
    )
    db.add(user)
    db.commit()

    # Verify stat increases accurately without fabrication
    updated_stats = AdminService.get_real_stats(db)
    assert updated_stats["total_users"] == 1

    # Cleanup
    db.close()
