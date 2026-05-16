from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie

from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.auth_service import AuthService
from app.core.dependencies import get_auth_service


router = APIRouter(prefix='/auth', tags=['Auth Service'])


@router.post(
    '/register',
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    new_user = await auth_service.register_user(user_data)

    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with that email address alredy exists'
        )

    return new_user


@router.post('/login')
async def login(
    login_data: UserLogin,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong email or password"
        )

    tokens = await auth_service.create_token_pair(user)

    response.set_cookie(
        key='refresh_token',
        value=tokens['refresh_token'],
        httponly=True,
        samesite='lax',
        secure=False,  # for HTTP reqs
        max_age=30 * 24 * 60 * 60,
    )

    return {
        'access_token': tokens['access_token'],
        'token_type': 'bearer',
    }


@router.post('/refresh')
async def refresh_token_route(
    response: Response,
    refresh_token: str | None = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='The refresh token is missing. Please log in again.',
        )

    new_tokens = await auth_service.refresh_access_token(refresh_token)

    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='The refresh token is invalid or has expired. Please log in again.',
        )

    response.set_cookie(
        key='refresh_token',
        value=new_tokens['refresh_token'],
        httponly=True,
        samesite='lax',
        secure=False,  # fot HTTP
        max_age=30 * 24 * 60 * 60,
    )

    return {
        'access_token': new_tokens['access_token'],
        'token_type': 'bearer',
    }
