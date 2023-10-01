from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

page_router = APIRouter(
	tags=["Pages"],
	dependencies=[],
	responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")


@page_router.get("/",  response_class=HTMLResponse)
async def auth_template(request: Request):
	return templates.TemplateResponse("auth_panel.html", context={"request": request})
