import pymysql
import base64
import gerencProdutos

from mangum import Mangum
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from database import get_db

templates = Jinja2Templates(directory="front/templates")

app = FastAPI()
app.mount("/front", StaticFiles(directory="front"), name="view")
app.include_router(gerencProdutos.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    #if request.session.get("user_logged_in"):
        #return RedirectResponse(url="/mainpage", status_code=303)

    #login_error = request.session.pop("login_error", None)
    #show_login_modal = request.session.pop("show_login_modal", False)

    return templates.TemplateResponse("index.html", {
        "request": request#,
        #"login_error": login_error,
        #"show_login_modal": "block" if show_login_modal else "none"
    })

@app.get("/CadastroLoja", response_class=HTMLResponse)
async def cadastroLoja(request: Request):

    return templates.TemplateResponse("cadastroLoja.html", {
        "request": request
    })


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

@app.get("/mainpage", name="mainpage", response_class=HTMLResponse)
async def mainpage(request: Request, db = Depends(get_db)):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        sql_produtos = """
            SELECT Id_Produto, Nome, Preco, Qtd_Estoque 
            FROM Produto 
            WHERE fk_Loja_Id_Loja = 1 AND Status = 1
            ORDER BY Nome
        """
        cursor.execute(sql_produtos)
        produtos = cursor.fetchall()

        for prod in produtos:
            sql_imagens = "SELECT Imagem FROM Imagem_Produto WHERE fk_Produto_Id_Produto = %s"
            cursor.execute(sql_imagens, (prod["Id_Produto"],))
            imagens_blob = cursor.fetchall()
            
            prod["lista_imagens"] = [
                base64.b64encode(img["Imagem"]).decode('utf-8') 
                for img in imagens_blob if img["Imagem"]
            ]

    return templates.TemplateResponse("mainpage.html", {
        "request": request, 
        "produtos": produtos
    })

@app.get("/produto/{id_produto}")
async def detalhes_produto(request: Request, id_produto: int, db = Depends(get_db)):
    # Usamos o DictCursor para devolver os dados em formato de dicionário
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # 1. Procurar os dados principais do Produto
        sql_produto = "SELECT Id_Produto, Nome, Preco, Qtd_Estoque FROM Produto WHERE Id_Produto = %s"
        cursor.execute(sql_produto, (id_produto,))
        produto = cursor.fetchone()
        
        if not produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        # 2. Procurar as imagens associadas a este produto
        sql_imagens = "SELECT Imagem FROM Imagem_Produto WHERE fk_Produto_Id_Produto = %s"
        cursor.execute(sql_imagens, (id_produto,))
        imagens_blob = cursor.fetchall()
        
        # 3. Converter as imagens de BLOB para Base64
        produto["lista_imagens"] = [
            base64.b64encode(img["Imagem"]).decode('utf-8') 
            for img in imagens_blob if img["Imagem"]
        ]

    # Renderizar o template passando o dicionário do produto
    return templates.TemplateResponse(
        "visualizacao.html", 
        {"request": request, "produto": produto}
    )

handler = Mangum(app)