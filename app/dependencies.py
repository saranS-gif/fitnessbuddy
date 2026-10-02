from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.utils.security import decode_access_token
from app.models.user import User
from app.models.admin import Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login", auto_error=False)


def get_token_from_request(request: Request, bearer_token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    """Retrieve JWT token from Authorization header or HTTP cookies."""
    if bearer_token:
        return bearer_token
    token = request.cookies.get("fitbuddy_token")
    if token and token.startswith("Bearer "):
        return token.split(" ")[1]
    return token


def get_current_admin(
    token: Optional[str] = Depends(get_token_from_request),
    db: Session = Depends(get_db)
) -> Optional[Admin]:
    """Resolves authenticated admin from JWT payload."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or not payload.get("is_admin"):
        return None
    admin_id = payload.get("sub")
    if not admin_id:
        return None
    return db.query(Admin).filter(Admin.id == int(admin_id)).first()


def require_admin(
    admin: Optional[Admin] = Depends(get_current_admin)
) -> Admin:
    """Enforces administrator authorization."""
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Administrator authentication required."
        )
    return admin
