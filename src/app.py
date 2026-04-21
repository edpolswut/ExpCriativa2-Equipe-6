import pymysql
import base64
import gerencProdutos

from mangum import Mangum
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from database import get_db

#Hash
def gerar_hash(senha: str) -> str:
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=64,
        salt=salt,
        iterations=100_000,
    )

    hash_bytes = kdf.derive(senha.encode())

    # junta salt + hash e codifica
    return base64.b64encode(salt + hash_bytes).decode()


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    decoded = base64.b64decode(hash_salvo.encode())

    salt = decoded[:16]
    hash_original = decoded[16:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=64,
        salt=salt,
        iterations=100_000,
    )

    try:
        kdf.verify(senha.encode(), hash_original)
        return True
    except Exception:
        return False

templates = Jinja2Templates(directory="front/templates")

app = FastAPI()

from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="teste123")

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

@app.get("/cadastro", response_class=HTMLResponse)
async def cadastro(request: Request):
    return templates.TemplateResponse("cadastro.html", {
        "request": request
    })

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request
    })

@app.get("/CadastroLoja", response_class=HTMLResponse)
async def cadastroLoja(request: Request):

    return templates.TemplateResponse("cadastroLoja.html", {
        "request": request
    })

@app.get("/perfilLojista", response_class=HTMLResponse)
async def perfil(request: Request, db = Depends(get_db)):
    # Pega o ID do usuário da sessão
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # 1. Busca os dados do usuário
        cursor.execute("SELECT Nome, Email FROM Usuario WHERE Id_Usuario = %s", (user_id,))
        usuario = cursor.fetchone()

        # 2. Busca as lojas associadas a este usuário (usando a tabela Usuario_Perfil)
        # Trazemos apenas lojas ativas (Status = 1)
        sql_lojas = """
            SELECT L.*, UP.fk_Perfil_Id_Perfil, P.Nom_Perfil
            FROM Loja L
            INNER JOIN Usuario_Perfil UP ON L.Id_Loja = UP.fk_Loja_Id_Loja
            INNER JOIN Perfil P ON UP.fk_Perfil_Id_Perfil = P.Id_Perfil
            WHERE UP.fk_Usuario_Id_Usuario = %s AND L.Status = 1
        """
        cursor.execute(sql_lojas, (user_id,))
        lojas = cursor.fetchall()

    # Passamos a lista de lojas para o HTML
    return templates.TemplateResponse(
        request=request,
        name="perfilLojista.html",
        context={
            "request": request,
            "usuario": usuario,
            "lojas": lojas
        }
    )

@app.post("/CriarLoja", name="CriarLoja")
async def CriarLoja(
    request: Request,
    NomeLoja: str = Form(...),
    EmailLoja: str = Form(...),
    CNPJ: str = Form(...),
    Telefone: str = Form(...),
    CEP: str = Form(...),
    Logradouro: str = Form(...), # Usaremos como 'Rua'
    Numero: int = Form(...),
    Cidade: str = Form(...),
    Bairro: str = Form(...),
    Complemento: str = Form(None),
    db = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    try:
        with db.cursor() as cursor:
            # 1. Inserir na tabela Loja
            # Nota: Usei NomeLoja como Razao_Social por padrão, ajuste se necessário.
            sql_loja = """
                INSERT INTO Loja (Nome, Cnpj, Razao_Social, Email, Telefone, Status) 
                VALUES (%s, %s, %s, %s, %s, 1)
            """
            cursor.execute(sql_loja, (NomeLoja, CNPJ, NomeLoja, EmailLoja, Telefone))
            id_loja = cursor.lastrowid

            # 2. Inserir na tabela Usuario_Perfil 
            # fk_Perfil_Id_Perfil = 2 (Lojista)
            sql_perfil = """
                INSERT INTO Usuario_Perfil (fk_Perfil_Id_Perfil, fk_Usuario_Id_Usuario, fk_Loja_Id_Loja) 
                VALUES (2, %s, %s)
            """
            cursor.execute(sql_perfil, (user_id, id_loja))

            # 3. Inserir na tabela Endereco
            sql_endereco = """
                INSERT INTO Endereco (fk_Usuario_Id_Usuario, fk_Loja_Id_Loja, Cep, Rua, Numero, Cidade, Bairro, Complemento, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
            """
            cursor.execute(sql_endereco, (
                user_id, id_loja, CEP, Logradouro, Numero, Cidade, Bairro, Complemento
            ))

            db.commit()
            return RedirectResponse(url="/perfilLojista", status_code=303)

    except Exception as e:
        print(f"Erro ao criar loja e endereço: {e}")
        db.rollback() # Cancela tudo se der erro
        return RedirectResponse(url="/CadastroLoja?erro=1", status_code=303)
    finally:
        db.close()

from fastapi import UploadFile, File

# --- ROTA GET: Busca todos os dados (Loja, Endereço e Configurações) ---
@app.get("/EditarLoja/{id_loja}", response_class=HTMLResponse)
async def editar_loja(request: Request, id_loja: int, db = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # Busca dados da Loja
        cursor.execute("SELECT * FROM Loja WHERE Id_Loja = %s", (id_loja,))
        loja = cursor.fetchone()

        # Busca Endereço
        cursor.execute("SELECT * FROM Endereco WHERE fk_Loja_Id_Loja = %s", (id_loja,))
        endereco = cursor.fetchone()

        # Busca Configurações Visuais
        cursor.execute("SELECT * FROM Config_Loja WHERE fk_Loja_Id_Loja = %s", (id_loja,))
        config = cursor.fetchone()

        if config:
            if config.get("Logo"):
                config["Logo_B64"] = base64.b64encode(config["Logo"]).decode('utf-8')
            if config.get("Banner"):
                config["Banner_B64"] = baseSafeb64encode(config["Banner"]).decode('utf-8')

    return templates.TemplateResponse(
        request=request,
        name="editarLoja.html",
        context={
            "request": request, 
            "loja": loja, 
            "endereco": endereco,
            "config": config,
            "id_loja": id_loja
        }
    )

# --- ROTA POST: Salva todas as alterações ---
@app.post("/SalvarEdicaoLoja")
async def salvar_edicao_loja(
    request: Request,
    Id_Loja: int = Form(...),
    Nome: str = Form(...),
    Razao_Social: str = Form(...),
    Cnpj: str = Form(...),
    Email: str = Form(...),
    Telefone: str = Form(...),
    # Endereço
    Cep: str = Form(...),
    Rua: str = Form(...),
    Numero: int = Form(...),
    Cidade: str = Form(...),
    Bairro: str = Form(...),
    Complemento: str = Form(None),
    # Configurações
    Nom_Tema: str = Form(...),
    Cor_Principal: str = Form(...),
    Cor_Secundaria: str = Form(...),
    Url: str = Form(...),
    Logo: UploadFile = File(None),
    Banner: UploadFile = File(None),
    db = Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            # 1. Atualiza Loja
            cursor.execute("""
                UPDATE Loja SET Nome=%s, Cnpj=%s, Razao_Social=%s, Email=%s, Telefone=%s 
                WHERE Id_Loja=%s
            """, (Nome, Cnpj, Razao_Social, Email, Telefone, Id_Loja))

            # 2. Atualiza Endereço
            cursor.execute("""
                UPDATE Endereco SET Cep=%s, Rua=%s, Numero=%s, Cidade=%s, Bairro=%s, Complemento=%s 
                WHERE fk_Loja_Id_Loja=%s
            """, (Cep, Rua, Numero, Cidade, Bairro, Complemento, Id_Loja))

            # 3. Atualiza ou Insere Config_Loja
            cursor.execute("SELECT Id_Config_Loja FROM Config_Loja WHERE fk_Loja_Id_Loja=%s", (Id_Loja,))
            existe_config = cursor.fetchone()

            logo_data = await Logo.read() if Logo and Logo.filename else None
            banner_data = await Banner.read() if Banner and Banner.filename else None

            if existe_config:
                cursor.execute("""
                    UPDATE Config_Lo_ja SET Nom_Tema=%s, Cor_Principal=%s, Cor_Secundaria=%s, Url=%s 
                    WHERE fk_Loja_Id_Loja=%s
                """, (Nom_Tema, Cor_Principal, Cor_Secundaria, Url, Id_Loja))
                if logo_data:
                    cursor.execute("UPDATE Config_Loja SET Logo=%s WHERE fk_Loja_Id_Loja=%s", (logo_data, Id_Loja))
                if banner_data:
                    cursor.execute("UPDATE Config_Loja SET Banner=%s WHERE fk_Loja_Id_Loja=%s", (banner_data, Id_Loja))
            else:
                cursor.execute("""
                    INSERT INTO Config_Loja (fk_Loja_Id_Loja, Nom_Tema, Cor_Principal, Cor_Secundaria, Url, Logo, Banner)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (Id_Loja, Nom_Tema, Cor_Principal, Cor_Secundaria, Url, logo_data or b'', banner_data or b''))

            db.commit()
            return RedirectResponse(url=f"/EditarLoja/{Id_Loja}?sucesso=1", status_code=303)
    except Exception as e:
        db.rollback()
        print(f"Erro ao salvar: {e}")
        return RedirectResponse(url=f"/EditarLoja/{Id_Loja}?erro=1", status_code=303)


#Insert de usuário
@app.post("/CriarUsuario", name="CriarUsuario")
async def CriarUsuario(
    request: Request,
    Nome: str = Form(...),
    CPF: str = Form(...), 
    Email: str = Form(...), 
    Senha: str = Form(...), 
    db = Depends(get_db)
):
    try:
        with db.cursor() as cursor:

            cursor.execute("SELECT Email FROM Usuario WHERE Email = %s", (Email,)) # executa um comando SQL, %s é um placeholder para evitar SQL injection
            if cursor.fetchone():   
                return RedirectResponse(url="/forms", status_code=303)

            senha_hash = gerar_hash(Senha)

            sql = "INSERT INTO Usuario (Nome, Cpf, Email, Senha_Hash, Dat_Criacao, Status) VALUES (%s, %s, %s, %s, current_date(), 1)"
            cursor.execute(sql, (Nome, CPF, Email, senha_hash))
            db.commit()

            return RedirectResponse(url="/", status_code=303)

    except Exception as e: 
        print("ERRO AO CRIAR USUARIO:", e)
        return RedirectResponse(url="/", status_code=303)

    finally:
        db.close()

#Login
@app.post("/Login")
async def Login(
    request: Request,
    Email: str = Form(...),
    Senha: str = Form(...),
    db = Depends(get_db)
):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Usuario WHERE Email = %s", (Email,))
            usuario = cursor.fetchone()

            if not usuario:
                return RedirectResponse(url="/login?erro=1", status_code=303)

            if not verificar_senha(Senha, usuario["Senha_Hash"]):
                return RedirectResponse(url="/login?erro=1", status_code=303)

            request.session["user_id"] = usuario["Id_Usuario"]
            request.session["user_nome"] = usuario["Nome"]

            return RedirectResponse(url="/perfilLojista", status_code=303)

    except Exception as e:
        print("ERRO VERIFY:", e)
        return False


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

handler = Mangum(app)