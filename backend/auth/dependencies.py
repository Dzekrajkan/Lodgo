from fastapi import Depends, HTTPException, Request
from jose import jwt
from sqlalchemy.orm import Session
from backend import models
from backend.database import get_db
from backend.auth import service as auth_service

def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = auth_service.verify_token(access_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user