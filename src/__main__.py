import uvicorn
import argparse
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from users.router import user_router
from auth.router import auth_router
from auth import auth_service

app = FastAPI(title='AuthApi')

origins = [
	"http://localhost:3005",
	"https://localhost:3005",
	"http://localhost",
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--template", required=False, action=argparse.BooleanOptionalAction)
args = parser.parse_args()

if args.template:
	app.mount("/static", StaticFiles(directory="static"), name="static")
	templates = Jinja2Templates(directory="templates")

	@app.get("/", tags=["Template"], response_class=HTMLResponse)
	async def auth_template(request: Request):
		return templates.TemplateResponse("auth_panel.html", context={"request": request})


app.include_router(user_router)
app.include_router(auth_router)

if __name__ == '__main__':
	uvicorn.run('__main__:app', host="localhost", port=3000, reload=True)
