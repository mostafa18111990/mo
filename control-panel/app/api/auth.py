from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from ..schemas.user import UserOut
from ..core.security import hash_password, verify_password, create_access_token, get_current_user
from ..core.audit import audit

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Annotated[Session, Depends(get_db)]):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        role=UserRole.customer,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    audit(db, "user.register", actor_id=user.id, target_type="user", target_id=user.id)
    db.commit()
    return user


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
