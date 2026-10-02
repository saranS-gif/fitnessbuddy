import json
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        user = User(
            name=user_in.name.strip(),
            age=user_in.age,
            weight=user_in.weight,
            goal=user_in.goal,
            intensity=user_in.intensity,
            experience=user_in.experience,
            workout_location=user_in.workout_location,
            preferred_days=json.dumps(user_in.preferred_days)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def list_all(db: Session) -> List[User]:
        return db.query(User).order_by(User.created_at.desc()).all()

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        user = UserService.get_by_id(db, user_id)
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
