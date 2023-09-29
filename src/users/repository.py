from typing import List

from database import (
	Database,
	BaseRepository,
	RepositoryException
)
from models import (
	User,
    Role,
    RoleNameEnum
)

from .schema import (
	LiteUser,
	UserCreate,
	UserUpdate
)


class UserRepository(BaseRepository):
	def __init__(self, db: Database):
		super().__init__(db, User)

	def get_all(self, skip: int = 0, limit: int = 100) -> List[LiteUser]:
		return super().get_all(skip, limit)

	def create(self, obj_in: UserCreate) -> User:
		db_obj: User = User(**dict(obj_in))
		role_obj = self.db.query(Role).filter(Role.name == RoleNameEnum.USER.value).first()

		if not role_obj:
			raise RepositoryException(status_code=500, message='Role [User] or default role not created')

		db_obj.roles.append(role_obj)
		self.db.add(db_obj)
		self.db.commit()
		self.db.refresh(db_obj)
		return db_obj

	def get_by_id(self, user_id: int) -> LiteUser:
		return super().get_by_id(user_id)

	def update(self, obj_id: int, obj_in: UserUpdate) -> LiteUser:
		return super().update(obj_id, obj_in)

	def delete(self, user_id: int) -> LiteUser:
		return super().delete(user_id)
