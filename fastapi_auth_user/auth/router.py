from fastapi import APIRouter, Depends, status

from .user_forms import AuthUserDataForm, ResetUserPasswordDataForm
from ..database import db_helper, Database
from ..users.schema import Token, UserAuth, LiteUser
from .service import AuthenticationService

auth_router = APIRouter(
	prefix='/api',
	tags=["Authentication"],
	dependencies=[],
	responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

auth_service = AuthenticationService(next(db_helper.session_dependency()))


@auth_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login_user(
		user_data: AuthUserDataForm = Depends(AuthUserDataForm.as_form),
):
	user_data.email = user_data.username if user_data.email is None else user_data.email
	return auth_service.get_access_token(user_data)


@auth_router.get("/profile/me", response_model=UserAuth, status_code=status.HTTP_201_CREATED)
def get_user_by_token(
		token: str = Depends(auth_service.oauth2_scheme),
):
	return auth_service.get_user_by_token(token)


@auth_router.post("/reset-password", response_model=LiteUser, status_code=status.HTTP_201_CREATED)
def reset_password(
		token: str = Depends(auth_service.oauth2_scheme),
		user_data: ResetUserPasswordDataForm = Depends(ResetUserPasswordDataForm.as_form),
):
	return auth_service.reset_password(token, user_data.new_password)
