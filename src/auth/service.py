from datetime import datetime, timedelta
from typing import Optional

from config import settings
from database import Database
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from models import User
from passlib.context import CryptContext
from users.repository import UserRepository
from users.schema import Token, UserAuth


class AuthenticationService:

	def __init__(self):
		self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
		self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

	def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
		to_encode = data.copy()
		if expires_delta:
			expire = datetime.utcnow() + expires_delta
		else:
			expire = datetime.utcnow() + timedelta(minutes=60)
		to_encode.update({"exp": expire})

		encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
		token: Token = Token(access_token=encoded_jwt)

		return token

	def password_hash(self, password: str) -> str:
		return self.pwd_context.hash(password)

	def verify_password(self, plain_password: str, hashed_password: str) -> bool:
		return self.pwd_context.verify(plain_password, hashed_password)

	def get_access_token(self, db: Database, user_data: OAuth2PasswordRequestForm) -> Token:
		try:
			user = UserRepository(db).get_user_by_email(user_data.username)

			if not self.verify_password(user_data.password, user.password):
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wrong password")

			user_dict = UserAuth.from_orm(user).dict()
			token: Token = self.create_access_token(data=user_dict)
			return token

		except Exception as err:
			raise err

	def get_user_by_token(self, db: Database, token: str) -> User:
		try:
			payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

			if payload is None:
				raise HTTPException(
					status_code=status.HTTP_401_UNAUTHORIZED,
					detail="Invalid authentication credentials",
					headers={"WWW-Authenticate": "Bearer"},
				)

			user = UserRepository(db).get_user_by_email(payload.get('email'))
			if user is None:
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
			return user

		except JWTError:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid authentication credentials",
				headers={"WWW-Authenticate": "Bearer"},
			)


auth_service = AuthenticationService()