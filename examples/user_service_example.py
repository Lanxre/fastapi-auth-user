from fastapi_auth_user.models import RoleNameEnum
from fastapi_auth_user.users import user_service
from fastapi_auth_user.users.schema import UserCreate, UserTokenResponse, UserRoles

if __name__ == "__main__":
	user: UserCreate = UserCreate(name="SomeName", email="Some_name@gmail.com", password="Aa1!LongPassword")
	user_response: UserTokenResponse = user_service.create(user)
	user_roles: UserRoles = user_service.add_role_for_user(user_response.id, RoleNameEnum.ADMIN)

