from __future__ import annotations

from app.core.security import hash_password, verify_password
from app.models.user import User


def test_password_is_hashed_and_verifiable():
    plain_password = "Password@123"
    hashed_password = hash_password(plain_password)

    assert hashed_password != plain_password
    assert verify_password(plain_password, hashed_password)


def test_register_login_and_me(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "vaibhav",
            "email": "vaibhav@example.com",
            "password": "Password@123",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["username"] == "vaibhav"
    assert "password" not in register_response.json()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username_or_email": "vaibhav",
            "password": "Password@123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "vaibhav@example.com"


def test_duplicate_username_is_rejected(client):
    first_response = client.post(
        "/api/auth/register",
        json={
            "username": "duplicate",
            "email": "duplicate1@example.com",
            "password": "Password@123",
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/auth/register",
        json={
            "username": "duplicate",
            "email": "duplicate2@example.com",
            "password": "Password@123",
        },
    )

    assert second_response.status_code == 409


def test_forgot_and_reset_password(client, db_session):
    user = User(
        username="reset-user",
        email="reset@example.com",
        password=hash_password("Password@123"),
        role="USER",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    forgot_response = client.post(
        "/api/auth/forgot-password",
        json={"email": "reset@example.com"},
    )

    assert forgot_response.status_code == 200
    reset_token = forgot_response.json()["reset_token"]
    assert reset_token

    reset_response = client.post(
        "/api/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": "NewPassword@123",
        },
    )

    assert reset_response.status_code == 200

    login_response = client.post(
        "/api/auth/login",
        json={
            "username_or_email": "reset-user",
            "password": "NewPassword@123",
        },
    )

    assert login_response.status_code == 200

def test_login_rate_limit(client):
    from app.core.rate_limit import _attempts

    _attempts.clear()
    try:
        for attempt in range(5):
            response = client.post(
                "/api/auth/login",
                json={
                    "username_or_email": "unknown_user",
                    "password": "WrongPassword@123",
                },
            )
            assert response.status_code == 401, f"Attempt {attempt + 1}: {response.status_code}"

        response = client.post(
            "/api/auth/login",
            json={
                "username_or_email": "unknown_user",
                "password": "WrongPassword@123",
            },
        )
        assert response.status_code == 429
    finally:
        _attempts.clear()
