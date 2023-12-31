from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from .user_forms import AuthUserDataForm
from ..logger import FastApiAuthLogger, LogLevel
from ..config import settings
from ..database import Database, RepositoryException
from ..models import User
from ..users.repository import UserRepository
from ..users.schema import Token, UserAuth, UserTokenResponse, Tokens, RefreshToken


class AuthenticationService:

	def __init__(self, db: Database):
		self.__db = db
		self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
		self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", scheme_name='scheme_name')
		self.__logger = FastApiAuthLogger("auth service", LogLevel.INFO)

	def create_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> Token:
		to_encode = data.copy()
		if expires_delta:
			expire = datetime.utcnow() + expires_delta
		else:
			expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
		to_encode.update({"exp": expire})

		encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
		token: Token = Token(token=encoded_jwt, token_time=expire)

		return token

	def password_hash(self, password: str) -> str:
		return self.pwd_context.hash(password)

	def verify_password(self, plain_password: str, hashed_password: str) -> bool:
		return self.pwd_context.verify(plain_password, hashed_password)

	def get_tokens(self, user_data: AuthUserDataForm) -> Tokens:
		try:
			user = UserRepository(self.__db).get_user_by_email(user_data.email)

			if user is None:
				self.__logger.error(f"Method[{self.get_tokens.__name__}]" +
				                    f"(There is no user with that e-mail:[{user_data.email}] address): Error")

				raise RepositoryException(
					status_code=status.HTTP_404_NOT_FOUND,
					message=f'There is no user with that e-mail address.'
				)

			if not self.verify_password(user_data.password, user.password):
				self.__logger.error(f"Method[{self.get_tokens.__name__}](Wrong password): Error")
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
				                    detail="Wrong password")

			user_dict = UserAuth.from_orm(user).dict()
			access_token: Token = self.create_token(data=user_dict)
			refresh_token: Token = self.create_token(data=user_dict,
			                                         expires_delta=timedelta(
				                                         hours=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

			tokens: Tokens = Tokens(access_token=access_token, refresh_token=refresh_token)
			self.__logger.info(f"Method[{self.get_tokens.__name__}]: Success")
			return tokens

		except RepositoryException as err:
			raise err

		except HTTPException as http_err:
			self.__logger.error(f"Method[{self.get_tokens.__name__}]({str(http_err)}): Error")
			raise http_err

		except Exception as err:
			self.__logger.error(f"Method[{self.get_tokens.__name__}]({str(err)}): Error")
			raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			                    detail="Internal server error")

	def get_user_by_token(self, token: str) -> User:
		try:
			payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

			if payload is None:
				self.__logger.error(f"Method[{self.get_user_by_token.__name__}](Payload is None): Error")
				raise HTTPException(
					status_code=status.HTTP_401_UNAUTHORIZED,
					detail="Invalid authentication credentials",
					headers={"WWW-Authenticate": "Bearer"},
				)

			user = UserRepository(self.__db).get_user_by_email(payload.get('email'))
			if user is None:
				self.__logger.error(f"Method[{self.get_user_by_token.__name__}]" +
				                    f"(User with email={payload.get('email')}): Error")

				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
				                    detail="User not found")

			self.__logger.info(f"Method[{self.get_user_by_token.__name__}]: Success")
			return user

		except JWTError:

			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid authentication credentials",
				headers={"WWW-Authenticate": "Bearer"},
			)

	def reset_password(self, token: str, new_password: str) -> UserTokenResponse:
		try:
			hashed_password = self.password_hash(new_password)
			user: User = self.get_user_by_token(token)
			updated_user = UserRepository(self.__db).set_password(user.id, hashed_password)
			self.__logger.info(f"Method[{self.reset_password.__name__}]: Success")
			return updated_user
		except RepositoryException as err:
			self.__logger.error(f"Method[{self.reset_password.__name__}]({str(err)}): Error")
			raise err

	def refresh_access_token(self, token: RefreshToken) -> Token:
		try:
			user: User = self.get_user_by_token(token.refresh_token)
			user_dict = UserAuth.from_orm(user).dict()
			access_token: Token = self.create_token(user_dict)
			self.__logger.info(f"Method[{self.refresh_access_token.__name__}]: Success")
			return access_token

		except Exception as err:
			self.__logger.error(f"Method[{self.refresh_access_token.__name__}]({str(err)}): Error")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
			                    detail="User not found")
