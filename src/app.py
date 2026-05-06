import pymysql
import base64
import gerencLoja
import gerencProdutos
import loja
import usuario
import auth

from mangum import Mangum
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import get_db
from templates import templates

app = FastAPI()

app.add_middleware(
    SessionMiddleware, 
    secret_key="SnapshopSecretKey1234567890",
    session_cookie="Snapshop_session",
    max_age = 600, # (em segundos)
    same_site="lax",
    https_only=False
)

app.mount("/front", StaticFiles(directory="front"), name="view")

# Routers
app.include_router(usuario.router)
app.include_router(gerencLoja.router)
app.include_router(gerencProdutos.router)
app.include_router(loja.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request
    })

@app.get("/sobre", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("sobre.html", {
        "request": request
    })

handler = Mangum(app)