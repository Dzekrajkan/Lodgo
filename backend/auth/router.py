from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
from backend import models
from backend.auth import email_utils, schemas
from backend.auth import service as auth_service
from backend.auth.dependencies import get_current_user
from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_SECURE, REFRESH_TOKEN_EXPIRE_DAYS
from backend.database import get_db
from backend.schemas import MessageOut

router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/refresh", response_model=MessageOut)
def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="You are not logged in.")

    try:
        payload = auth_service.verify_token(refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    new_access_token = auth_service.create_access_token({"sub": user_id})

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=COOKIE_SECURE,
        samesite="lax",
    )

    return {"success": "Access token refreshed"}

@router.post("/register", response_model=MessageOut, status_code=201)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_by_email = db.query(models.User).filter(models.User.email == user.email).first()
    if user_by_email:
        raise HTTPException(status_code=400, detail="Email is already in use")

    new_user = models.User(
        email=user.email,
        username=user.username,
        password_hash=auth_service.hash_password(user.password1),
        is_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = auth_service.create_verification_token(new_user.id)
    await email_utils.send_verification_email(new_user.email, token)

    return {"success": "Registration successful, confirmation email sent to email"}

@router.post("/login", response_model=MessageOut)
async def login(response: Response, data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")
    if not auth_service.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password or login")
    if not user.is_verified:
        raise HTTPException(403, "Email not confirmed")

    access_token = auth_service.create_access_token({"sub": str(user.id)})
    refresh_token = auth_service.create_refresh_token({"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=COOKIE_SECURE,
        samesite="lax",
    )

    return {"success": "Logged in successfully"}

@router.post("/logout", response_model=MessageOut)
async def logout(response: Response):
    response.delete_cookie("access_token", httponly=True, samesite="lax", path="/")
    response.delete_cookie("refresh_token", httponly=True, samesite="lax", path="/")
    return {"success": "Logout successful"}

@router.get("/auth/verify", response_model=MessageOut)
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = auth_service.verify_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="The token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

    if payload.get("type") != "email_verify":
        raise HTTPException(status_code=400, detail="Invalid token type")

    user_id = int(payload["sub"])
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(400, "This user does not exist.")

    user.is_verified = True
    db.commit()

    return {"success": "Your email has been confirmed. Now log in to your account."}

@router.get("/me", response_model=schemas.UserMeOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user