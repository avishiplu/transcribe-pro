import asyncio

from app.models.user import User
from app.repositories.users import (
    build_user_for_create,
    create_user,
    normalize_email,
)


class DummyAsyncSession:
    def __init__(self):
        self.added_user = None
        self.committed = False
        self.refreshed_user = None

    def add(self, user):
        self.added_user = user

    async def commit(self):
        self.committed = True

    async def refresh(self, user):
        self.refreshed_user = user


def test_normalize_email_strips_spaces_and_lowercases():
    assert normalize_email("  USER@Example.COM  ") == "user@example.com"


def test_build_user_for_create_returns_user_model():
    user = build_user_for_create(
        email="USER@Example.COM",
        password_hash="hashed-password",
    )

    assert isinstance(user, User)
    assert user.email == "user@example.com"
    assert user.password_hash == "hashed-password"
    assert user.id


def test_create_user_adds_commits_and_refreshes_user():
    db = DummyAsyncSession()

    user = asyncio.run(
        create_user(
            db=db,
            email="USER@Example.COM",
            password_hash="hashed-password",
        )
    )

    assert db.added_user == user
    assert db.committed is True
    assert db.refreshed_user == user
    assert user.email == "user@example.com"
