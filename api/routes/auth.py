import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.core.security import create_access_token, DEFAULT_EXPIRE_MINUTES

router = APIRouter(tags=["auth"])

DEFAULT_USERNAME = os.getenv("AUTH_USERNAME", "admin")
DEFAULT_PASSWORD = os.getenv("AUTH_PASSWORD", "secret")


def authenticate_user(username: str, password: str) -> bool:
    return username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD


@router.post("/auth/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_in_minutes = int(os.getenv("AUTH_TOKEN_EXPIRE_MINUTES", str(DEFAULT_EXPIRE_MINUTES)))
    access_token = create_access_token(
        subject=form_data.username,
        expires_delta=timedelta(minutes=expires_in_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer", "expires_in": expires_in_minutes * 60}
