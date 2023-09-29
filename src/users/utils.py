from typing import Optional

from database import Database
from models import User


class UserUtils:

	@staticmethod
	def get_user_by_email(db: Database, email: Optional[str] = None) -> User:
		if email is not None:
			return db.query(User).filter(User.email == email).first()
