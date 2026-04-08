import pymysql
import base64

from mangum import Mangum
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import date, datetime

# Configuração de templates Jinja2
templates = Jinja2Templates(directory="front/templates")

app = FastAPI();
app.mount("/front", StaticFiles(directory="front"), name="view")

# Configuração do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "abc123",
    "database": "SnapShop"
}

# Função para obter conexão com MySQL
def get_db():
    return pymysql.connect(**DB_CONFIG)

@app.get("/forms", response_class=HTMLResponse)
async def forms(request: Request):

    return templates.TemplateResponse("forms.html", {
        "request": request
    })


# Função exemplo de request do banco de dados
@app.post("/CriarUsuario", name="CriarUsuario")
async def CriarUsuario(
    request: Request,
    Nome: str = Form(...), 
    Email: str = Form(...), 
    Senha: str = Form(...), 
    db = Depends(get_db)
):
    try:
        with db.cursor() as cursor:

            cursor.execute("SELECT Email FROM Usuario WHERE Email = %s", (Email)) # executa um comando SQL, %s é um placeholder para evitar SQL injection
            if cursor.fetchone():
                return RedirectResponse(url="/forms", status_code=303)

            sql = "INSERT INTO Usuario (Nome, Email, Senha_Hash, Dat_Criacao, Cpf, Status) VALUES (%s, %s, %s, current_date(), 1, 1)"
            cursor.execute(sql, (Nome, Email, Senha))
            db.commit()

            return RedirectResponse(url="/forms", status_code=303)

    except Exception as e:
        return RedirectResponse(url="/forms", status_code=303)

    finally:
        db.close()

# Função exemplo de request do banco de dados
@app.get("/mainpage", name="mainpage", response_class=HTMLResponse)
async def mainpage(
    request: Request,
    db = Depends(get_db)
):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # Consulta SQL para produtos, incluindo uma imagem (se existir)
        sql = """
            SELECT P.Id_Produto, P.fk_Loja_Id_Loja, P.Nome, P.Preco, P.Qtd_Estoque, P.Status,
                   (SELECT IP.Imagem FROM Imagem_Produto IP WHERE IP.fk_Produto_Id_Produto = P.Id_Produto LIMIT 1) AS Imagem
            FROM Produto AS P
            ORDER BY P.Nome
        """
        cursor.execute(sql)
        produtos = cursor.fetchall()  # lista de dicts com dados dos produtos

    # Processa os dados (converte imagem para base64 se necessário)
    for prod in produtos:
        # Converter imagem blob para base64 (se houver)
        if prod["Imagem"]:
            prod["Imagem_base64"] = base64.b64encode(prod["Imagem"]).decode('utf-8')
        else:
            prod["Imagem_base64"] = None

    # nome_usuario = request.session.get("nome_usuario", None)
    # agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Renderiza o template 'mainpage.html' com os dados dos produtos
    return templates.TemplateResponse("mainpage.html", {
        "request": request,
        "produtos": produtos
    })

handler = Mangum(app)