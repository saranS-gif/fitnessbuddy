import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.user import UserCreate, UserOut
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user profile from onboarding."""
    try:
        user = UserService.create(db, user_in)
        # Parse preferred_days for response model
        pref_days = json.loads(user.preferred_days) if user.preferred_days else []
        return UserOut(
            id=user.id,
            name=user.name,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
            experience=user.experience,
            workout_location=user.workout_location,
            preferred_days=pref_days,
            created_at=user.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to create user: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Retrieve user profile by ID."""
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    pref_days = json.loads(user.preferred_days) if user.preferred_days else []
    return UserOut(
        id=user.id,
        name=user.name,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
        experience=user.experience,
        workout_location=user.workout_location,
        preferred_days=pref_days,
        created_at=user.created_at
    )
