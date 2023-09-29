from typing import List

from auth import RolePermissions
from database import (
	Database,
	db_helper
)
from fastapi import (
	APIRouter,
	Depends
)
from models import RoleNameEnum

from .schema import (
	UserCreate,
	UserTokenResponse,
	LiteUser,
	UserUpdate
)
from .service import UserService

user_router = APIRouter(
	prefix='/api',
	tags=["Users"],
	dependencies=[],
	responses={404: {"description": "Not found"}},
)

permissions_admin_moderator = RolePermissions([RoleNameEnum.ADMIN, RoleNameEnum.Moderator])
permissions_user = RolePermissions([RoleNameEnum.USER])


@user_router.get("/", response_model=List[LiteUser])
def get_users(
		skip: int = 0,
		limit: int = 10,
		db: Database = Depends(db_helper.session_dependency),
		access: bool = Depends(permissions_user.get_permissions)
):
	user_service = UserService(db)
	return user_service.get_all_users(skip, limit)


@user_router.get("/{user_id}", response_model=LiteUser)
def get_user(
		user_id: int = 1,
		db: Database = Depends(db_helper.session_dependency),
		access: bool = Depends(permissions_user.get_permissions)
):
	user_service = UserService(db)
	return user_service.get_by_id(user_id)


@user_router.post("/", response_model=UserTokenResponse, status_code=201)
def create_user(
		user: UserCreate,
		db: Database = Depends(db_helper.session_dependency),
		access: bool = Depends(permissions_admin_moderator.get_permissions)

):
	user_service = UserService(db)
	return user_service.create(user)


@user_router.patch("/{user_id}", response_model=UserTokenResponse)
def update_user(
		user_id: int,
		user: UserUpdate,
		db: Database = Depends(db_helper.session_dependency),
		access: bool = Depends(permissions_admin_moderator.get_permissions)
):
	user_service = UserService(db)
	return user_service.update(user_id, user)


@user_router.delete("/{user_id}", response_model=LiteUser)
def delete_user(
		user_id: int,
		db: Database = Depends(db_helper.session_dependency),
		access: bool = Depends(permissions_admin_moderator.get_permissions)
):
	user_service = UserService(db)
	return user_service.delete(user_id)
