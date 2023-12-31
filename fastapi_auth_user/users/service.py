from typing import List, Union

from fastapi import HTTPException
from fastapi import status

from ..logger import FastApiAuthLogger, LogLevel
from .repository import UserRepository
from .schema import UserCreate, LiteUser, UserTokenResponse, UserUpdate, UserRoles
from ..auth.permissions import auth_service
from ..database import Database, RepositoryException
from ..models import RoleNameEnum, User


class UserService:
	def __init__(self, db: Database):
		self.__db = db
		self.__logger = FastApiAuthLogger("user service", LogLevel.INFO)
		self._user_repository = UserRepository(db)

	@property
	def repository(self):
		return self._user_repository

	@repository.setter
	def repository(self, db: Database):
		self._user_repository = UserRepository(db)

	def get_all_users(self, skip: int = 0, limit: int = 100) -> List[LiteUser]:
		try:
			users = self._user_repository.get_all(skip, limit)
			self.__logger.info(f"Method[{self.get_all_users.__name__}]: Success")
			return users

		except RepositoryException as re:
			self.__logger.error(f"Method[{self.get_all_users.__name__}]({str(re.message)}): Error")
			raise HTTPException(status_code=re.status_code, detail=str(re.message))

		except HTTPException as http_err:
			self.__logger.error(f"Method[{self.get_all_users.__name__}]({str(http_err)}): Error")
			raise http_err

		except Exception as err:
			self.__logger.error(f"Method[{self.get_all_users.__name__}]({str(err.args[0])}): Error")
			raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			                    detail=str(err.args[0]))

	def create(self, user: UserCreate) -> UserTokenResponse:
		try:
			self.__is_user_exist(user)
			user.password = auth_service.password_hash(user.password)
			created_user = self._user_repository.create(user)
			user_token = self.__create_user_token_response(created_user)
			self.__logger.info(f"Method[{self.create.__name__}]: Success")
			return user_token

		except RepositoryException as re:
			self.__logger.error(f"Method[{self.create.__name__}]({str(re.message)}): Error")
			raise HTTPException(status_code=re.status_code, detail=str(re.message))

		except HTTPException as http_err:
			self.__logger.error(f"Method[{self.create.__name__}]({str(http_err)}): Error")
			raise http_err

		except Exception as err:
			self.__logger.error(f"Method[{self.create.__name__}]({str(err)}): Error")
			raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			                    detail=str(err))

	def get_by_id(self, user_id: int) -> LiteUser:
		try:
			user: LiteUser = self._user_repository.get_by_id(user_id)
			self.__logger.info(f"{self.get_by_id.__name__} Success")
			return user

		except HTTPException as http_err:
			self.__logger.error(f"Method[{self.get_by_id.__name__}]({str(http_err)}): Error")
			raise http_err

		except Exception as err:
			self.__logger.error(f"Method[{self.get_by_id.__name__}]({str(err)}): Error")
			raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			                    detail=str(err))

	def delete(self, user_id: int) -> LiteUser:
		try:
			user: LiteUser = self._user_repository.delete(user_id)
			self.__logger.info(f"Method[{self.delete.__name__}]: Success")
			return user

		except HTTPException as http_err:
			self.__logger.error(f"Method[{self.delete.__name__}]({str(http_err)}): Error")
			raise http_err

		except Exception as err:
			self.__logger.error(f"Method[{self.delete.__name__}]({str(err)}): Error")
			raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			                    detail=str(err))

	def update(self, user_id: int, user: UserUpdate) -> UserTokenResponse:
		try:
			self.__is_user_exist(user)
			if user.password is not None:
				user.password = auth_service.password_hash(user.password)
			updated_user: LiteUser = self._user_repository.update(user_id, user)
			user_token = self.__create_user_token_response(updated_user)
			self.__logger.info(f"{self.update.__name__} Success")
			return user_token

		except HTTPException as http_err:
			self.__logger.error(f"Method[{self.update.__name__}]({str(http_err)}): Error")
			raise http_err

		except Exception as err:
			self.__logger.error(f"Method[{self.update.__name__}]({str(err)}): Error")
			raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			                    detail=str(err))

	def get_user_roles(self, user_id: int) -> UserRoles:
		try:
			user = self._user_repository.get_by_id(user_id)
			user_roles: UserRoles = UserRoles.from_orm(user)
			self.__logger.info(f"{self.get_user_roles.__name__} Success")
			return user_roles
		except HTTPException as http_err:
			self.__logger.error(f"Method[{self.get_user_roles.__name__}]({str(http_err)}): Error")
			raise http_err

		except Exception as err:
			self.__logger.error(f"Method[{self.get_user_roles.__name__}]({str(err)}): Error")
			raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			                    detail="Cannot get role this user")

	def add_role_for_user(self, user_id: int, role: RoleNameEnum) -> UserRoles:
		try:
			user = self._user_repository.add_role(user_id, role)
			user_roles: UserRoles = UserRoles.from_orm(user)
			self.__logger.info(f"{self.add_role_for_user.__name__} Success")
			return user_roles
		except HTTPException as http_err:
			self.__logger.error(f"Method[{self.add_role_for_user.__name__}]({str(http_err)}): Error")
			raise http_err

		except Exception as err:
			self.__logger.error(f"Method[{self.add_role_for_user.__name__}]({str(err)}): Error")
			raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			                    detail=str(err))

	def delete_user_role(self, user_id: int, role: RoleNameEnum) -> UserRoles:
		try:
			user = self._user_repository.delete_role(user_id, role)
			user_roles: UserRoles = UserRoles.from_orm(user)
			self.__logger.info(f"{self.delete_user_role.__name__} Success")
			return user_roles
		except HTTPException as http_err:
			self.__logger.error(f"Method[{self.delete_user_role.__name__}]({str(http_err)}): Error")
			raise http_err

		except Exception as err:
			self.__logger.error(f"Method[{self.delete_user_role.__name__}]({str(err)}): Error")
			raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			                    detail=str(err))

	def has_role(self, user: User, role: RoleNameEnum) -> bool:
		for user_role in user.roles:
			if role.value == user_role.name:
				return True

		return False

	def __is_user_exist(self, user: Union[UserCreate, UserUpdate]):
		isExist = self._user_repository.get_user_by_email(user.email)
		if isExist is not None:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT,
			                    detail="Already exist with this email")

	def __create_user_token_response(self, user) -> UserTokenResponse:
		user_dict = UserCreate.from_orm(user).dict()
		access_token = auth_service.create_token(data=user_dict)
		user_token = UserTokenResponse(
			id=user.id,
			username=user.email,
			email=user.email,
			token=access_token,
		)
		return user_token
