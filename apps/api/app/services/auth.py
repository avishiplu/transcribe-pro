from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.users import create_user, get_user_by_email
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse


async def register_user(db: AsyncSession, request: UserRegisterRequest) -> UserResponse:
    existing_user = await get_user_by_email(db, request.email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    password_hash = hash_password(request.password)

    user = await create_user(
        db=db,
        email=request.email,
        password_hash=password_hash,
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        credit_balance=user.credit_balance,
    )


async def login_user(db: AsyncSession, request: UserLoginRequest) -> TokenResponse:
    user = await get_user_by_email(db, request.email)

    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(subject=user.id)

    return TokenResponse(access_token=access_token)
