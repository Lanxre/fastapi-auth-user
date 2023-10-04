from auth import auth_service
from auth.user_forms import AuthUserDataForm
from database import Database, db_helper
from fastapi import APIRouter, Request, Depends
from models import User, RoleNameEnum
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from users.schema import Token
from users import user_service


page_router = APIRouter(
	tags=["Pages"],
	dependencies=[],
	responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")


@page_router.get("/", response_class=HTMLResponse)
async def auth_page(request: Request):
	return templates.TemplateResponse("auth_panel.html", context={"request": request})


@page_router.post('/user-page', response_class=HTMLResponse)
async def user_page(
		request: Request,
		data_form: AuthUserDataForm = Depends(AuthUserDataForm.as_form),
		db: Database = Depends(db_helper.session_dependency)
):
	try:
		token: Token = auth_service.get_access_token(db, data_form)
		user: User = auth_service.get_user_by_token(db, token.access_token)

		users = []
		context = {
			"request": request,
			"token": token,
			"user": user
		}
		for user_role in user.roles:
			if RoleNameEnum.ADMIN.value == user_role.name:
				users = user_service.get_all_users()
				break

		if not users:
			return templates.TemplateResponse('user_panel.html', context=context)

		return templates.TemplateResponse('user_panel.html', context={
			"request": request,
			"token": token,
			"user": user,
			"users": users
		})

	except Exception as err:
		return templates.TemplateResponse('error_panel.html', context={
			"request": request,
			"error": err.args[0]
		})
