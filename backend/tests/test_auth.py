from datetime import datetime, timedelta, timezone
from jose import jwt
from backend.config import SECRET_KEY, ALGORITHM
from backend.auth.service import hash_password
from backend import models
import pytest

@pytest.fixture
def unverified_user(test_db):
    user = models.User(
        username="unverified",
        email="unverified@gmail.com",
        password_hash=hash_password("test1234"),
        is_verified=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    yield user

def test_register_success(client):
    password = "1234test"
    res = client.post("/api/register", json={"username": "test2", "email": "test2@gmail.com", "password1": password, "password2": password})

    assert res.status_code == 201

def test_register_duplicate_email(client, test_user):
    password = "1234test"
    res = client.post("/api/register", json={"username": "test", "email": "test@gmail.com", "password1": password, "password2": password})

    assert res.status_code == 400

def test_register_password_mismatch(client):
    res = client.post("/api/register", json={"username": "test2", "email": "test2@gmail.com", "password1": "test1234", "password2": "test1233"})

    assert res.status_code == 422

def test_login_success(client, test_user):
    res = client.post("/api/login", data={"username": "test@gmail.com", "password": "test1234"})
    assert res.status_code == 200

def test_login_wrong_password(client, test_user):
    res = client.post("/api/login", data={"username": "test@gmail.com", "password": "test1233"})
 
    assert res.status_code == 400
    assert res.json()["detail"] == "Incorrect password or login"

def test_login_unverified_email(client, unverified_user):
    res = client.post("/api/login", data={"username": "unverified@gmail.com", "password": "test1234"})
 
    assert res.status_code == 403
    assert res.json()["detail"] == "Email not confirmed"

def test_login_nonexistent_user(client):
    res = client.post("/api/login", data={"username": "nobody@gmail.com", "password": "test1234"})
 
    assert res.status_code == 400
    assert res.json()["detail"] == "User does not exist"

def test_logout(authorized_client):
    res = authorized_client.post("/api/logout")

    assert res.status_code == 200

def test_me_authenticated(authorized_client):
    res = authorized_client.get("/api/me")

    assert res.status_code == 200

def test_me_unauthenticated(client):
    res = client.get("/api/me")

    assert res.status_code == 401

def test_refresh_success(authorized_client):
    res = authorized_client.post("/api/refresh")

    assert res.status_code == 200

def test_refresh_expired_token(client):
    expired_payload = {
        "sub": "some-user-id",
        "type": "refresh",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }
    expired_token = jwt.encode(
        expired_payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    client.cookies.set("refresh_token", expired_token)
    res = client.post("/api/refresh")

    assert res.status_code == 401
    assert res.json()["detail"] == "Refresh token expired"

def test_refresh_invalid_token(client):
    client.cookies.set("refresh_token", "opwefewnpfwnwove")
    res = client.post("/api/refresh")
    
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid refresh token"