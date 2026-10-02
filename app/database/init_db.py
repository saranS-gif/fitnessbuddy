import logging
from app.database.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.workout import WorkoutPlan, PlanRevision
from app.models.feedback import Feedback
from app.models.admin import Admin
from app.utils.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """Create all tables in the database and seed default admin."""
    logger.info("Initializing FitBuddy database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created.")

    # Seed default admin if none exists
    db = SessionLocal()
    try:
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not existing_admin:
            default_admin = Admin(
                username="admin",
                password_hash=hash_password("admin123")
            )
            db.add(default_admin)
            db.commit()
            logger.info("Default administrator seeded (username: 'admin', password: 'admin123').")
    except Exception as e:
        logger.error(f"Error seeding admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
