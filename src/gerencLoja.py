import pymysql
import base64
import auth

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import UploadFile, File

from database import get_db
from templates import templates

router = APIRouter()

@router.get("/CadastroLoja", response_class=HTMLResponse)
async def cadastroLoja(request: Request):

    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("cadastroLoja.html", {
        "request": request
    })

@router.post("/CriarLoja", name="CriarLoja")
async def CriarLoja(
    request: Request,
    NomeLoja: str = Form(...),
    EmailLoja: str = Form(...),
    CNPJ: str = Form(...),
    Telefone: str = Form(...),
    CEP: str = Form(...),
    Logradouro: str = Form(...),
    Numero: int = Form(...),
    Cidade: str = Form(...),
    Bairro: str = Form(...),
    Complemento: str = Form(None),
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)
    
    user_id = request.session.get("user_id")

    try:
        with db.cursor() as cursor:
            sql_loja = """
                INSERT INTO Loja (Nome, Cnpj, Razao_Social, Email, Telefone, Status) 
                VALUES (%s, %s, %s, %s, %s, 1)
            """
            cursor.execute(sql_loja, (NomeLoja, CNPJ, NomeLoja, EmailLoja, Telefone))
            id_loja = cursor.lastrowid

            # fk_Perfil_Id_Perfil = 2 (Lojista)
            sql_perfil = """
                INSERT INTO Usuario_Perfil (fk_Perfil_Id_Perfil, fk_Usuario_Id_Usuario, fk_Loja_Id_Loja) 
                VALUES (2, %s, %s)
            """
            cursor.execute(sql_perfil, (user_id, id_loja))

            sql_endereco = """
                INSERT INTO Endereco (fk_Usuario_Id_Usuario, fk_Loja_Id_Loja, Cep, Rua, Numero, Cidade, Bairro, Complemento, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
            """
            cursor.execute(sql_endereco, (
                user_id, id_loja, CEP, Logradouro, Numero, Cidade, Bairro, Complemento
            ))

            db.commit()
            return JSONResponse(content={"sucesso": True})

    except Exception as e:
        print(f"Erro: {e}")
        db.rollback()
        return JSONResponse(status_code=500, content={"erro": "sistema"})
    finally:
        db.close()

@router.get("/EditarLoja/{id_loja}", response_class=HTMLResponse)
async def editar_loja(
    request: Request, 
    id_loja: int, 
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)
    
    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, id_loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM Loja WHERE Id_Loja = %s", (id_loja,))
        loja = cursor.fetchone()

        cursor.execute("SELECT * FROM Endereco WHERE fk_Loja_Id_Loja = %s", (id_loja,))
        endereco = cursor.fetchone()

        cursor.execute("SELECT * FROM Config_Loja WHERE fk_Loja_Id_Loja = %s", (id_loja,))
        config = cursor.fetchone()

        if config:
            if config.get("Logo"):
                config["Logo_B64"] = base64.b64encode(config["Logo"]).decode('utf-8')
            if config.get("Banner"):
                config["Banner_B64"] = base64.b64encode(config["Banner"]).decode('utf-8')

    return templates.TemplateResponse(
        request=request,
        name="gerencLoja/editarLoja.html",
        context={
            "request": request, 
            "loja": loja, 
            "endereco": endereco,
            "config": config,
            "id_loja": id_loja
        }
    )

@router.post("/SalvarEdicaoLoja")
async def salvar_edicao_loja(
    request: Request,
    Id_Loja: int = Form(...),
    Nome: str = Form(...),
    Razao_Social: str = Form(...),
    Cnpj: str = Form(...),
    Email: str = Form(...),
    Telefone: str = Form(...),
    Cep: str = Form(...),
    Rua: str = Form(...),
    Numero: int = Form(...),
    Cidade: str = Form(...),
    Bairro: str = Form(...),
    Complemento: str = Form(None),
    Nom_Tema: str = Form(...),
    Cor_Principal: str = Form(...),
    Cor_Secundaria: str = Form(...),
    Url: str = Form(...),
    Logo: UploadFile = File(None),
    Banner: UploadFile = File(None),
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)
    
    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, Id_Loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE Loja SET Nome=%s, Cnpj=%s, Razao_Social=%s, Email=%s, Telefone=%s 
                WHERE Id_Loja=%s
            """, (Nome, Cnpj, Razao_Social, Email, Telefone, Id_Loja))

            cursor.execute("""
                UPDATE Endereco SET Cep=%s, Rua=%s, Numero=%s, Cidade=%s, Bairro=%s, Complemento=%s 
                WHERE fk_Loja_Id_Loja=%s
            """, (Cep, Rua, Numero, Cidade, Bairro, Complemento, Id_Loja))

            cursor.execute("SELECT Id_Config_Loja FROM Config_Loja WHERE fk_Loja_Id_Loja=%s", (Id_Loja,))
            existe_config = cursor.fetchone()

            logo_data = await Logo.read() if Logo and Logo.filename else None
            banner_data = await Banner.read() if Banner and Banner.filename else None

            if existe_config:
                cursor.execute("""
                    UPDATE Config_Loja SET Nom_Tema=%s, Cor_Principal=%s, Cor_Secundaria=%s, Url=%s 
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

@router.get("/DeletarLoja/{id_loja}")
async def deletar_loja(
    request: Request, 
    id_loja: int, 
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)
    
    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, id_loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM Usuario_Perfil 
                WHERE fk_Usuario_Id_Usuario = %s AND fk_Loja_Id_Loja = %s
            """, (user_id, id_loja))
            
            if not cursor.fetchone():
                return RedirectResponse(url="/perfilLojista?erro=acesso_negado", status_code=303)

            cursor.execute("UPDATE Loja SET Status = 0 WHERE Id_Loja = %s", (id_loja,))
            db.commit()
            
        return RedirectResponse(url="/perfilLojista?sucesso=loja_excluida", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/EditarLoja/{id_loja}?erro=exclusao", status_code=303)
