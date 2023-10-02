from auth import auth_service
from database import Database, db_helper
from fastapi import APIRouter, Request, Depends
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from auth import auth_service
from models import User
from users.schema import Token

page_router = APIRouter(
	tags=["Pages"],
	dependencies=[],
	responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")


@page_router.get("/", response_class=HTMLResponse)
async def auth_page(request: Request):
	return templates.TemplateResponse("auth_panel.html", context={"request": request})


@page_router.post('/admin-page', response_class=HTMLResponse)
async def admin_page(
		request: Request,
		db: Database = Depends(db_helper.session_dependency)
):
	try:
		user_data_form = await request.form()
		token: Token = auth_service.get_access_token(db, user_data_form['email'])
		user: User = auth_service.get_user_by_token(db, token)

		return templates.TemplateResponse('auth_panel.html', context={
			"request": request,
			"token": token,
			"user": user
		})

	except Exception as err:
		return templates.TemplateResponse('error_panel', context={"error": err})
