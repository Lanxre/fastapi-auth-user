from fastapi_auth_user.database import db_helper
from fastapi_auth_user.auth.user_forms import AuthUserDataForm
from fastapi_auth_user.auth import auth_service
from fastapi_auth_user.users.schema import Token

if __name__ == "__main__":
	user_data: AuthUserDataForm = AuthUserDataForm()
	token: Token = auth_service.get_access_token(db_helper.session_dependency(), user_data)
	user = auth_service.get_user_by_token(db_helper.session_dependency(), token)
