from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.user import LoginRequest, TokenOut, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenOut)
def login(data: LoginRequest, db: DbSession):
    return AuthService(db).login(data.username, data.password)


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return user
