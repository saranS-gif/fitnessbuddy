import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("fitbuddy")

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    try:
        from app.models import User, WorkoutPlan, PlanRevision, Feedback
        Base.metadata.create_all(bind=engine)

        # Safe migration check for existing SQLite databases
        if "sqlite" in settings.DATABASE_URL:
            try:
                with engine.connect() as conn:
                    cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()]
                    if cols:
                        if "height" not in cols:
                            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN height FLOAT DEFAULT 170.0")
                        if "location" not in cols:
                            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN location VARCHAR(50) DEFAULT 'Home'")
                        if "equipment" not in cols:
                            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN equipment VARCHAR(100) DEFAULT 'None'")
                        conn.commit()
            except Exception as e:
                logger.warning(f"SQLite migration check warning: {e}")

        print("[FitBuddy] Database initialized")
    except Exception as e:
        logger.warning(f"[FitBuddy] Database initialization notice: {e}")


__all__ = ["engine", "SessionLocal", "Base", "get_db", "init_db"]
