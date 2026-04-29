import pymysql
import base64
import os
import auth

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# Cassiano vai alterar a autenticação.
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from database import get_db


templates = Jinja2Templates(directory="front/templates")
router = APIRouter()


@router.get("/cadastro", response_class=HTMLResponse)
async def cadastro(request: Request):
    return templates.TemplateResponse("cadastro.html", {
        "request": request
    })

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request
    })

@router.get("/perfilLojista", response_class=HTMLResponse)
async def perfil(request: Request, db = Depends(get_db)):

    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT Nome, Email FROM Usuario WHERE Id_Usuario = %s", (user_id,))
        usuario = cursor.fetchone()

        # apenas lojas ativas (Status = 1)
        sql_lojas = """
            SELECT L.*, UP.fk_Perfil_Id_Perfil, P.Nom_Perfil, CL.Logo
            FROM Loja L
            INNER JOIN Usuario_Perfil UP ON L.Id_Loja = UP.fk_Loja_Id_Loja
            INNER JOIN Perfil P ON UP.fk_Perfil_Id_Perfil = P.Id_Perfil
             LEFT JOIN Config_Loja CL ON L.Id_Loja = CL.fk_Loja_Id_Loja
            WHERE UP.fk_Usuario_Id_Usuario = %s AND L.Status = 1
        """
        cursor.execute(sql_lojas, (user_id,))
        lojas = cursor.fetchall()

        for loja in lojas:
            if loja.get("Logo"):
                loja["Logo_B64"] = base64.b64encode(loja["Logo"]).decode('utf-8')

    return templates.TemplateResponse(
        request=request,
        name="perfilLojista.html",
        context={
            "request": request,
            "usuario": usuario,
            "lojas": lojas
        }
    )

@router.post("/CriarUsuario", name="CriarUsuario")
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
            cursor.execute("SELECT Email FROM Usuario WHERE Email = %s", (Email,)) 
            if cursor.fetchone():   
                return JSONResponse(status_code=400, content={"erro": "email_existe"})
            
            cursor.execute("SELECT Cpf FROM Usuario WHERE Cpf = %s", (CPF,)) 
            if cursor.fetchone():   
                return JSONResponse(status_code=400, content={"erro": "cpf_existe"})

            senha_hash = gerar_hash(Senha)
            sql = "INSERT INTO Usuario (Nome, Cpf, Email, Senha_Hash, Dat_Criacao, Status) VALUES (%s, %s, %s, %s, current_date(), 1)"
            cursor.execute(sql, (Nome, CPF, Email, senha_hash))
            db.commit()

            return JSONResponse(content={"sucesso": True})
    except Exception:
        return JSONResponse(status_code=500, content={"erro": "sistema"})
    finally:
        db.close()

@router.post("/Login")
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

            if not usuario or not verificar_senha(Senha, usuario["Senha_Hash"]):
                return RedirectResponse(url="/login?erro=credenciais", status_code=303)

            request.session["user_id"] = usuario["Id_Usuario"]
            request.session["user_nome"] = usuario["Nome"]

            return RedirectResponse(url="/perfilLojista", status_code=303)

    except Exception as e:
        print("ERRO VERIFY:", e)
        return RedirectResponse(url="/login?erro=sistema", status_code=303)
    
@router.get("/EditarUsuario", response_class=HTMLResponse)
async def editar_usuario_form(request: Request, db = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT Nome, Email, Cpf FROM Usuario WHERE Id_Usuario = %s", (user_id,))
        usuario = cursor.fetchone()

    return templates.TemplateResponse("editarUsuario.html", {"request": request, "usuario": usuario})

@router.post("/SalvarEdicaoUsuario")
async def salvar_edicao_usuario(
    request: Request,
    Nome: str = Form(...),
    Email: str = Form(...),
    Senha: str = Form(None),
    db = Depends(get_db)
):
    user_id = request.session.get("user_id")
    try:
        with db.cursor() as cursor:
            sql = "UPDATE Usuario SET Nome=%s, Email=%s WHERE Id_Usuario=%s"
            cursor.execute(sql, (Nome, Email, user_id))
            
            if Senha and Senha.strip() != "":
                novo_hash = gerar_hash(Senha)
                cursor.execute("UPDATE Usuario SET Senha_Hash=%s WHERE Id_Usuario=%s", (novo_hash, user_id))
            
            db.commit()
            request.session["user_nome"] = Nome
        return RedirectResponse(url="/perfilLojista?sucesso=1", status_code=303)
    except Exception as e:
        print(f"Erro ao editar utilizador: {e}")
        return RedirectResponse(url="/EditarUsuario?erro=1", status_code=303)

@router.get("/DeletarUsuario")
async def deletar_usuario(request: Request, db = Depends(get_db)):
    user_id = request.session.get("user_id")
    
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    try:
        with db.cursor() as cursor:
            sql_lojas = """
                UPDATE Loja L
                INNER JOIN Usuario_Perfil UP ON L.Id_Loja = UP.fk_Loja_Id_Loja
                SET L.Status = 0
                WHERE UP.fk_Usuario_Id_Usuario = %s
            """
            cursor.execute(sql_lojas, (user_id,))

            cursor.execute("UPDATE Usuario SET Status = 0 WHERE Id_Usuario = %s", (user_id,))
            
            db.commit()
            
        request.session.clear() 
        return RedirectResponse(url="/?conta_eliminada=1", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        return RedirectResponse(url="/perfilLojista?erro=exclusao", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear() 
    return RedirectResponse(url="/login", status_code=303)

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