import pymysql
import base64
import gerencProdutos

from mangum import Mangum
from fastapi import APIRouter, FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
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

@router.get("/CadastroLoja", response_class=HTMLResponse)
async def cadastroLoja(request: Request):

    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("cadastroLoja.html", {
        "request": request
    })

@router.get("/perfilLojista", response_class=HTMLResponse)
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

@router.post("/CriarLoja", name="CriarLoja")
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
        return JSONResponse(status_code=401, content={"erro": "sessao_expirada"})

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
            return JSONResponse(content={"sucesso": True})

    except Exception as e:
        print(f"Erro: {e}")
        db.rollback()
        return JSONResponse(status_code=500, content={"erro": "sistema"})
    finally:
        db.close()

from fastapi import UploadFile, File

# --- ROTA GET: Busca todos os dados (Loja, Endereço e Configurações) ---
@router.get("/EditarLoja/{id_loja}", response_class=HTMLResponse)
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
                config["Banner_B64"] = base64.b64encode(config["Banner"]).decode('utf-8')

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
@router.post("/SalvarEdicaoLoja")
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
            # Verifica se email já existe
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

# Login
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

            # SE USUÁRIO NÃO EXISTIR OU SENHA ESTIVER ERRADA (Redireciona com erro)
            if not usuario or not verificar_senha(Senha, usuario["Senha_Hash"]):
                return RedirectResponse(url="/login?erro=credenciais", status_code=303)

            request.session["user_id"] = usuario["Id_Usuario"]
            request.session["user_nome"] = usuario["Nome"]

            return RedirectResponse(url="/perfilLojista", status_code=303)

    except Exception as e:
        print("ERRO VERIFY:", e)
        return RedirectResponse(url="/login?erro=sistema", status_code=303)
    
# --- ROTA GET: Carrega o formulário com os dados atuais do utilizador ---
@router.get("/EditarUsuario", response_class=HTMLResponse)
async def editar_usuario_form(request: Request, db = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT Nome, Email, Cpf FROM Usuario WHERE Id_Usuario = %s", (user_id,))
        usuario = cursor.fetchone()

    return templates.TemplateResponse("editarUsuario.html", {"request": request, "usuario": usuario})

# --- ROTA POST: Guarda as alterações (Nome, Email e Opcionalmente Senha) ---
@router.post("/SalvarEdicaoUsuario")
async def salvar_edicao_usuario(
    request: Request,
    Nome: str = Form(...),
    Email: str = Form(...),
    Senha: str = Form(None), # Senha é opcional na edição
    db = Depends(get_db)
):
    user_id = request.session.get("user_id")
    try:
        with db.cursor() as cursor:
            # Atualiza dados básicos
            sql = "UPDATE Usuario SET Nome=%s, Email=%s WHERE Id_Usuario=%s"
            cursor.execute(sql, (Nome, Email, user_id))
            
            # Se o utilizador preencheu uma nova senha, gera o hash e atualiza
            if Senha and Senha.strip() != "":
                novo_hash = gerar_hash(Senha)
                cursor.execute("UPDATE Usuario SET Senha_Hash=%s WHERE Id_Usuario=%s", (novo_hash, user_id))
            
            db.commit()
            request.session["user_nome"] = Nome # Atualiza o nome na sessão
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
            # 1. Desativa as lojas vinculadas a este usuário
            sql_lojas = """
                UPDATE Loja L
                INNER JOIN Usuario_Perfil UP ON L.Id_Loja = UP.fk_Loja_Id_Loja
                SET L.Status = 0
                WHERE UP.fk_Usuario_Id_Usuario = %s
            """
            cursor.execute(sql_lojas, (user_id,))

            # 2. Desativa o próprio usuário
            cursor.execute("UPDATE Usuario SET Status = 0 WHERE Id_Usuario = %s", (user_id,))
            
            db.commit()
            
        request.session.clear() 
        return RedirectResponse(url="/?conta_eliminada=1", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        return RedirectResponse(url="/perfilLojista?erro=exclusao", status_code=303)

@router.get("/DeletarLoja/{id_loja}")
async def deletar_loja(request: Request, id_loja: int, db = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM Usuario_Perfil 
                WHERE fk_Usuario_Id_Usuario = %s AND fk_Loja_Id_Loja = %s
            """, (user_id, id_loja))
            
            if not cursor.fetchone():
                return RedirectResponse(url="/perfilLojista?erro=acesso_negado", status_code=303)

            # Desativa a loja (Status = 0)
            cursor.execute("UPDATE Loja SET Status = 0 WHERE Id_Loja = %s", (id_loja,))
            db.commit()
            
        return RedirectResponse(url="/perfilLojista?sucesso=loja_excluida", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/EditarLoja/{id_loja}?erro=exclusao", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear() 
    return RedirectResponse(url="/login", status_code=303)

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