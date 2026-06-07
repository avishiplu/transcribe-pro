from datetime import timedelta

from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password


def test_hash_password_does_not_store_plain_text():
    plain_password = "safe-password-123"

    hashed_password = hash_password(plain_password)

    assert hashed_password != plain_password
    assert verify_password(plain_password, hashed_password)


def test_verify_password_rejects_wrong_password():
    hashed_password = hash_password("correct-password")

    assert not verify_password("wrong-password", hashed_password)


def test_create_access_token_contains_subject():
    token = create_access_token(
        subject="user-123",
        expires_delta=timedelta(minutes=5),
    )

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == "user-123"
