import pymysql
import base64
import auth

from typing import List, Optional
from fastapi import APIRouter, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.usuario import coresAvatarUsuario, obterAvatarUsuario
from database import get_db
from templates import templates

router = APIRouter()

@router.get("/loja/{identificador}/login", response_class=HTMLResponse)
async def login_loja(request: Request, identificador: str, db = Depends(get_db)):
    """Formulário de login específico da loja"""
    # Se já está logado, vai direto para a loja
    if request.session.get("user_logged_in"):
        return RedirectResponse(url=f"/loja/{identificador}/home", status_code=303)
    
    # Busca dados da loja para exibição
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        if identificador.isdigit():
            sql_loja = """
                SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                FROM Loja L 
                LEFT JOIN Config_Loja C ON L.Id_Loja = C.fk_Loja_Id_Loja 
                WHERE L.Id_Loja = %s AND L.Status = 1
            """
            cursor.execute(sql_loja, (int(identificador),))
        else:
            sql_loja = """
                SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                FROM Config_Loja C 
                INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja 
                WHERE C.Url = %s AND L.Status = 1
            """
            cursor.execute(sql_loja, (identificador,))
        
        loja = cursor.fetchone()
    
    if not loja:
        return RedirectResponse(url="/", status_code=303)
    
    if loja.get("Logo"):
        loja["Logo_B64"] = base64.b64encode(loja["Logo"]).decode('utf-8')
    
    return templates.TemplateResponse("loja/loginLoja.html", {
        "request": request,
        "loja": loja,
        "identificador": identificador,
        "categorias_selecionadas": [],
        "busca_atual": None,
        "preco_selecionado": None,
        "obterAvatarUsuario": obterAvatarUsuario
    })


@router.post("/loja/{identificador}/login", response_class=HTMLResponse)
async def processar_login_loja(
    request: Request, 
    identificador: str,
    Email: str = Form(...), 
    Senha: str = Form(...),
    db = Depends(get_db)
):
    """Processa login específico da loja"""
    # Se já está logado, desloga primeiro
    if request.session.get("user_logged_in"):
        request.session.clear()
    
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Usuario WHERE UPPER(Email) = UPPER(%s) AND Senha_Hash = MD5(%s)", (Email, Senha))
            usuario = cursor.fetchone()

            if not usuario:
                return RedirectResponse(url=f"/loja/{identificador}/login?erro=credenciais", status_code=303)
            
            cursor.execute("SELECT 1 FROM Usuario_Perfil WHERE fk_Usuario_Id_Usuario = %s AND fk_Perfil_Id_Perfil = 1", (usuario["Id_Usuario"],))
            Admin = cursor.fetchone()

            # Armazena na sessão
            request.session["user_id"] = usuario["Id_Usuario"]
            request.session["user_nome"] = usuario["Nome"]
            request.session["user_perfil"] = "Administrador" if Admin else "Lojista"
            request.session["user_logged_in"] = True
            request.session["user_Avatar"] = bool(usuario["Imagem_Usuario"])
            request.session["user_Avatar_Inicial"] = usuario["Nome"][0].upper()
            request.session["user_Avatar_Cor"] = coresAvatarUsuario[ord(usuario["Nome"][0].upper()) % len(coresAvatarUsuario)]

            return RedirectResponse(url=f"/loja/{identificador}/home", status_code=303)

    except Exception as e:
        print("ERRO LOGIN LOJA:", e)
        return RedirectResponse(url=f"/loja/{identificador}/login?erro=sistema", status_code=303)


@router.get("/loja/{identificador}/logout")
async def logout_loja(request: Request, identificador: str):
    """Logout específico da loja"""
    request.session.clear()
    return RedirectResponse(url=f"/loja/{identificador}/home", status_code=303)


# ==================== ROTAS DE CADASTRO DE USUÁRIO NA LOJA ====================

@router.get("/loja/{identificador}/cadastro", response_class=HTMLResponse)
async def cadastro_loja_usuario(request: Request, identificador: str, db = Depends(get_db)):
    """Formulário de cadastro de usuário específico da loja"""
    if request.session.get("user_logged_in"):
        return RedirectResponse(url=f"/loja/{identificador}", status_code=303)
    
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        if identificador.isdigit():
            sql_loja = """
                SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                FROM Loja L 
                LEFT JOIN Config_Loja C ON L.Id_Loja = C.fk_Loja_Id_Loja 
                WHERE L.Id_Loja = %s AND L.Status = 1
            """
            cursor.execute(sql_loja, (int(identificador),))
        else:
            sql_loja = """
                SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                FROM Config_Loja C 
                INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja 
                WHERE C.Url = %s AND L.Status = 1
            """
            cursor.execute(sql_loja, (identificador,))
        
        loja = cursor.fetchone()
    
    if not loja:
        return RedirectResponse(url="/", status_code=303)
    
    if loja.get("Logo"):
        loja["Logo_B64"] = base64.b64encode(loja["Logo"]).decode('utf-8')
    
    return templates.TemplateResponse("loja/cadastro.html", {
        "request": request,
        "loja": loja,
        "identificador": identificador,
        "categorias_selecionadas": [],
        "busca_atual": None,
        "preco_selecionado": None,
        "obterAvatarUsuario": obterAvatarUsuario
    })

@router.post("/loja/{identificador}/cadastro", response_class=HTMLResponse)
async def processar_cadastro_loja_usuario(
    request: Request,
    identificador: str,
    Nome: str = Form(...),
    CPF: str = Form(...), 
    Email: str = Form(...), 
    Senha: str = Form(...),
    DataNascimento: str = Form(...),
    db = Depends(get_db)
):
    """Processa o cadastro de usuário específico da loja"""
    if request.session.get("user_logged_in"):
        request.session.clear()
    
    try:
        with db.cursor() as cursor:
            # Verifica se o email já existe
            cursor.execute("SELECT 1 FROM Usuario WHERE UPPER(Email) = UPPER(%s)", (Email,)) 
            if cursor.fetchone():
                return RedirectResponse(url=f"/loja/{identificador}/cadastro?erro=email_existe", status_code=303)
            
            # Verifica se o CPF já existe
            cursor.execute("SELECT 1 FROM Usuario WHERE Cpf = %s", (CPF,)) 
            if cursor.fetchone():
                return RedirectResponse(url=f"/loja/{identificador}/cadastro?erro=cpf_existe", status_code=303)

            # Insere o novo usuário
            sql = "INSERT INTO Usuario (Nome, Cpf, Email, Senha_Hash, Dat_Nascimento, Dat_Criacao, Status) VALUES (%s, %s, %s, MD5(%s), %s, current_date(), 1)"
            cursor.execute(sql, (Nome, CPF, Email, Senha, DataNascimento))
            db.commit()

            # Redireciona para a página de login da loja com mensagem de sucesso
            return RedirectResponse(url=f"/loja/{identificador}/login?sucesso=cadastro", status_code=303)
            
    except Exception as e:
        print(f"ERRO CADASTRO LOJA USUARIO: {e}")
        db.rollback()
        return RedirectResponse(url=f"/loja/{identificador}/cadastro?erro=sistema", status_code=303)
    finally:
        db.close()


# ==================== FIM ROTAS DE CADASTRO DE USUÁRIO NA LOJA ====================



@router.get("/loja/{identificador}/produtos", name="vitrine_loja", response_class=HTMLResponse)
async def vitrine_loja(
    request: Request, 
    identificador: str,
    busca: Optional[str] = None,
    categorias: List[int] = Query(None),
    preco: Optional[str] = None,
    db = Depends(get_db)
):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # 1. Verifica se è um ID ou Texto(Url)
        if identificador.isdigit():
            sql_loja = """
                SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                FROM Loja L 
                LEFT JOIN Config_Loja C ON L.Id_Loja = C.fk_Loja_Id_Loja 
                WHERE L.Id_Loja = %s AND L.Status = 1
            """
            cursor.execute(sql_loja, (int(identificador),))
        else:
            sql_loja = """
                SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                FROM Config_Loja C 
                INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja 
                WHERE C.Url = %s AND L.Status = 1
            """
            cursor.execute(sql_loja, (identificador,))
            
        loja = cursor.fetchone()
        
        if not loja:
            return RedirectResponse(url="/", status_code=303)
            
        
        if loja.get("Logo"):
            loja["Logo_B64"] = base64.b64encode(loja["Logo"]).decode('utf-8')
        if loja.get("Banner"):
            loja["Banner_B64"] = base64.b64encode(loja["Banner"]).decode('utf-8')

        
        sql_categorias_loja = "SELECT Id_Categoria, Nome FROM Categoria WHERE fk_Loja_Id_Loja = %s AND Status = 1"
        cursor.execute(sql_categorias_loja, (loja["Id_Loja"],))
        categorias_loja = cursor.fetchall()

        
        sql_produtos_base = """
            SELECT DISTINCT P.Id_Produto, P.Nome, P.Preco, P.Qtd_Estoque 
            FROM Produto P
        """
        where_clauses = ["P.fk_Loja_Id_Loja = %s", "P.Status = 1"]
        params = [loja["Id_Loja"]]
        
        # Filtro de Categoria
        if categorias:
            sql_produtos_base += " INNER JOIN Produto_Categoria PC ON P.Id_Produto = PC.fk_Produto_Id_Produto"
            placeholders = ', '.join(['%s'] * len(categorias))
            where_clauses.append(f"PC.fk_Categoria_Id_Categoria IN ({placeholders})")
            params.extend(categorias)
            
        # Filtro de Busca por Nome
        if busca:
            where_clauses.append("P.Nome LIKE %s")
            params.append(f"%{busca}%")
            
        # Filtro de Preço
        if preco:
            if preco == "0-100":
                where_clauses.append("P.Preco <= 100")
            elif preco == "100-200":
                where_clauses.append("P.Preco > 100 AND P.Preco <= 200")
            elif preco == "200-300":
                where_clauses.append("P.Preco > 200 AND P.Preco <= 300")
            elif preco == "300-plus":
                where_clauses.append("P.Preco > 300")

        sql_produtos = sql_produtos_base + " WHERE " + " AND ".join(where_clauses) + " ORDER BY P.Nome"
        cursor.execute(sql_produtos, params)
        produtos = cursor.fetchall()

        # Busca imagens para cada produto filtrado
        for prod in produtos:
            sql_imagens = "SELECT Imagem FROM Imagem_Produto WHERE fk_Produto_Id_Produto = %s"
            cursor.execute(sql_imagens, (prod["Id_Produto"],))
            imagens_blob = cursor.fetchall()
            prod["lista_imagens"] = [
                base64.b64encode(img["Imagem"]).decode('utf-8') 
                for img in imagens_blob if img["Imagem"]
            ]

    return templates.TemplateResponse("loja/mainpage.html", {
        "request": request, 
        "loja": loja,
        "produtos": produtos,
        "categorias_loja": categorias_loja,
        "busca_atual": busca,
        "categorias_selecionadas": categorias or [],
        "preco_selecionado": preco,
        "obterAvatarUsuario": obterAvatarUsuario
    })

@router.get("/loja/{identificador}/produto/{id_produto}", response_class=HTMLResponse)
async def detalhes_produto(request: Request, identificador: str, id_produto: int, db = Depends(get_db)):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        sql_produto = "SELECT * FROM Produto WHERE Id_Produto = %s"
        cursor.execute(sql_produto, (id_produto,))
        produto = cursor.fetchone()
        
        if not produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        sql_imagens = "SELECT Imagem FROM Imagem_Produto WHERE fk_Produto_Id_Produto = %s"
        cursor.execute(sql_imagens, (id_produto,))
        imagens_blob = cursor.fetchall()
        produto["lista_imagens"] = [
            base64.b64encode(img["Imagem"]).decode('utf-8') 
            for img in imagens_blob if img["Imagem"]
        ]

        sql_loja = """
            SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
            FROM Loja L 
            LEFT JOIN Config_Loja C ON L.Id_Loja = C.fk_Loja_Id_Loja 
            WHERE L.Id_Loja = %s AND L.Status = 1
        """
        cursor.execute(sql_loja, (produto["fk_Loja_Id_Loja"],))
        loja = cursor.fetchone()
        
        if not loja:
            return RedirectResponse(url="/", status_code=303)

        if loja and loja.get("Logo"):
            loja["Logo_B64"] = base64.b64encode(loja["Logo"]).decode('utf-8')

        sql_categorias = """
            SELECT C.Nome
            FROM Categoria C
            INNER JOIN Produto_Categoria PC
                ON PC.fk_Categoria_Id_Categoria = C.Id_Categoria
            WHERE PC.fk_Produto_Id_Produto = %s
        """
        cursor.execute(sql_categorias, (id_produto,))
        produto["categorias"] = [c["Nome"] for c in cursor.fetchall()]

    return templates.TemplateResponse("loja/visualizacao.html", {
        "request": request, 
        "produto": produto,
        "loja": loja,
            "identificador": identificador,
        "categorias_selecionadas": [],
        "busca_atual": None,
        "preco_selecionado": None,
        "obterAvatarUsuario": obterAvatarUsuario
    })

# ==================== ROTA DA HOMEPAGE ====================

@router.get("/loja/{identificador}/home", name="homepage_loja", response_class=HTMLResponse)
async def homepage_loja(
    request: Request, 
    identificador: str,
    busca: Optional[str] = None,
    categorias: List[int] = Query(None),
    preco: Optional[str] = None,
    db = Depends(get_db)
):
    """Exibe a Homepage da loja com Banner, Carrossel de destaques e filtros"""
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # 1. Verifica se é um ID ou Texto(Url) e busca a Loja (com Banner e Logo)
        if identificador.isdigit():
            sql_loja = """
                SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                FROM Loja L 
                LEFT JOIN Config_Loja C ON L.Id_Loja = C.fk_Loja_Id_Loja 
                WHERE L.Id_Loja = %s AND L.Status = 1
            """
            cursor.execute(sql_loja, (int(identificador),))
        else:
            sql_loja = """
                SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                FROM Config_Loja C 
                INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja 
                WHERE C.Url = %s AND L.Status = 1
            """
            cursor.execute(sql_loja, (identificador,))
            
        loja = cursor.fetchone()
        
        if not loja:
            return RedirectResponse(url="/", status_code=303)
            
        # Converte as imagens da loja para Base64
        if loja.get("Logo"):
            loja["Logo_B64"] = base64.b64encode(loja["Logo"]).decode('utf-8')
        if loja.get("Banner"):
            loja["Banner_B64"] = base64.b64encode(loja["Banner"]).decode('utf-8')

        # 2. Busca Categorias para a barra lateral
        sql_categorias_loja = "SELECT Id_Categoria, Nome FROM Categoria WHERE fk_Loja_Id_Loja = %s AND Status = 1"
        cursor.execute(sql_categorias_loja, (loja["Id_Loja"],))
        categorias_loja = cursor.fetchall()

        # 3. Busca TODOS os Produtos (com aplicação de filtros)
        sql_produtos_base = """
            SELECT DISTINCT P.Id_Produto, P.Nome, P.Preco, P.Qtd_Estoque 
            FROM Produto P
        """
        where_clauses = ["P.fk_Loja_Id_Loja = %s", "P.Status = 1"]
        params = [loja["Id_Loja"]]
        
        # Filtro de Categoria
        if categorias:
            sql_produtos_base += " INNER JOIN Produto_Categoria PC ON P.Id_Produto = PC.fk_Produto_Id_Produto"
            placeholders = ', '.join(['%s'] * len(categorias))
            where_clauses.append(f"PC.fk_Categoria_Id_Categoria IN ({placeholders})")
            params.extend(categorias)
            
        # Filtro de Busca por Nome
        if busca:
            where_clauses.append("P.Nome LIKE %s")
            params.append(f"%{busca}%")
            
        # Filtro de Preço
        if preco:
            if preco == "0-100":
                where_clauses.append("P.Preco <= 100")
            elif preco == "100-200":
                where_clauses.append("P.Preco > 100 AND P.Preco <= 200")
            elif preco == "200-300":
                where_clauses.append("P.Preco > 200 AND P.Preco <= 300")
            elif preco == "300-plus":
                where_clauses.append("P.Preco > 300")

        sql_produtos = sql_produtos_base + " WHERE " + " AND ".join(where_clauses) + " ORDER BY P.Nome"
        cursor.execute(sql_produtos, params)
        produtos = cursor.fetchall()

        # Busca todas as imagens para a grade de produtos (mantém o slider dos cards funcionando)
        for prod in produtos:
            sql_imagens = "SELECT Imagem FROM Imagem_Produto WHERE fk_Produto_Id_Produto = %s"
            cursor.execute(sql_imagens, (prod["Id_Produto"],))
            imagens_blob = cursor.fetchall()
            prod["lista_imagens"] = [
                base64.b64encode(img["Imagem"]).decode('utf-8') 
                for img in imagens_blob if img["Imagem"]
            ]

        # 4. Busca 8 Produtos Aleatórios EXCLUSIVAMENTE para o Carrossel
        sql_aleatorios = """
            SELECT Id_Produto, Nome, Preco, Qtd_Estoque 
            FROM Produto 
            WHERE fk_Loja_Id_Loja = %s AND Status = 1
            ORDER BY RAND() LIMIT 8
        """
        cursor.execute(sql_aleatorios, (loja["Id_Loja"],))
        produtos_aleatorios = cursor.fetchall()

        # Busca todas as imagens para os produtos do carrossel
        for prod_aleatorio in produtos_aleatorios:
            sql_imagens_aleat = "SELECT Imagem FROM Imagem_Produto WHERE fk_Produto_Id_Produto = %s"
            cursor.execute(sql_imagens_aleat, (prod_aleatorio["Id_Produto"],))
            imagens_blob_aleat = cursor.fetchall()
            prod_aleatorio["lista_imagens"] = [
                base64.b64encode(img["Imagem"]).decode('utf-8') 
                for img in imagens_blob_aleat if img["Imagem"]
            ]

    # Retorna chamando a nova página homepage.html criada anteriormente
    return templates.TemplateResponse("loja/homepage.html", {
        "request": request, 
        "loja": loja,
        "produtos": produtos,
        "produtos_aleatorios": produtos_aleatorios,
        "categorias_loja": categorias_loja,
        "busca_atual": busca,
        "categorias_selecionadas": categorias or [],
        "preco_selecionado": preco,
        "obterAvatarUsuario": obterAvatarUsuario
    })


# ==================== ROTAS DE CARRINHO ====================

@router.get("/loja/{identificador}/carrinho", response_class=HTMLResponse)
async def exibir_carrinho(request: Request, identificador: str, db = Depends(get_db)):
    """Exibe o carrinho da loja específica"""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url=f"/loja/{identificador}/login", status_code=303)

    loja = None
    itens_carrinho = []
    total_produtos = 0.0

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Busca dados da loja
            if identificador.isdigit():
                sql_loja = """
                    SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                    FROM Loja L 
                    LEFT JOIN Config_Loja C ON L.Id_Loja = C.fk_Loja_Id_Loja 
                    WHERE L.Id_Loja = %s AND L.Status = 1
                """
                cursor.execute(sql_loja, (int(identificador),))
            else:
                sql_loja = """
                    SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url 
                    FROM Config_Loja C 
                    INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja 
                    WHERE C.Url = %s AND L.Status = 1
                """
                cursor.execute(sql_loja, (identificador,))
            
            loja_info = cursor.fetchone()
            
            if not loja_info:
                return RedirectResponse(url="/", status_code=303)

            # Prepara o Logo e mantém o objeto original para preservar cores e configurações
            if loja_info.get("Logo"):
                loja_info["Logo_B64"] = base64.b64encode(loja_info["Logo"]).decode('utf-8')
            
            loja = loja_info

            # Busca o carrinho do usuário para esta loja específica
            sql_carrinho = """
                SELECT c.Id_Carrinho, l.Id_Loja, l.Nome 
                FROM Carrinho c
                INNER JOIN Loja l ON c.fk_Loja_Id_Loja = l.Id_Loja
                WHERE c.fk_Usuario_Id_Usuario = %s AND c.fk_Loja_Id_Loja = %s
                ORDER BY c.Id_Carrinho DESC LIMIT 1
            """
            cursor.execute(sql_carrinho, (user_id, loja_info["Id_Loja"]))
            carrinho = cursor.fetchone()

            if carrinho:
                # Busca os itens do carrinho
                sql_itens = """
                    SELECT p.Id_Produto, p.Nome, p.Preco, p.Qtd_Estoque, cp.Qtd_Produto,
                    (SELECT Imagem 
                        FROM Imagem_Produto 
                            WHERE fk_Produto_Id_Produto = p.Id_Produto LIMIT 1) AS Imagem
                    FROM Carrinho_Produto cp
                    INNER JOIN Produto p ON cp.fk_Produto_Id_Produto = p.Id_Produto
                    WHERE cp.fk_Carrinho_Id_Carrinho = %s
                """
                cursor.execute(sql_itens, (carrinho["Id_Carrinho"],))
                itens_banco = cursor.fetchall()

                # Processa itens
                for item in itens_banco:
                    imagem_b64 = None
                    if item.get("Imagem"):
                        imagem_b64 = base64.b64encode(item["Imagem"]).decode('utf-8')
                    
                    total_produtos += item["Preco"] * item["Qtd_Produto"]
                    
                    itens_carrinho.append({
                        "Id_Produto": item["Id_Produto"],
                        "Nome": item["Nome"],
                        "Preco": item["Preco"],
                        "Qtd_Estoque": item["Qtd_Estoque"],
                        "Qtd_Produto": item["Qtd_Produto"],
                        "Imagem_B64": imagem_b64
                    })
            # BUSCAR ENDEREÇOS DO USUÁRIO
            enderecos = []
            if loja:
                sql_enderecos = "SELECT * FROM Endereco WHERE fk_Usuario_Id_Usuario = %s AND fk_Loja_Id_Loja = %s AND Status = 1"
                cursor.execute(sql_enderecos, (user_id, loja["Id_Loja"]))
                enderecos = cursor.fetchall()

    except Exception as e:
        print(f"ERRO AO CARREGAR CARRINHO: {e}")
    finally:
        db.close()

    return templates.TemplateResponse("loja/carrinho.html", {
        "request": request,
        "loja": loja,
        "itens_carrinho": itens_carrinho,
        "total_produtos": total_produtos,
        "total_compra": total_produtos,
        "identificador": identificador,
        "categorias_selecionadas": [],
        "busca_atual": None,
        "preco_selecionado": None,
        "obterAvatarUsuario": obterAvatarUsuario,
        "enderecos": enderecos
    })


@router.post("/loja/{identificador}/carrinho/adicionar/{id_produto}", response_class=HTMLResponse)
async def adicionar_carrinho(
    request: Request, 
    identificador: str, 
    id_produto: int, 
    quantidade: int = 1,
    db = Depends(get_db)
):
    """Adiciona um produto ao carrinho da loja específica"""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url=f"/loja/{identificador}/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Validar se a loja existe
            if identificador.isdigit():
                sql_loja = "SELECT Id_Loja FROM Loja WHERE Id_Loja = %s AND Status = 1"
                cursor.execute(sql_loja, (int(identificador),))
            else:
                sql_loja = "SELECT L.Id_Loja FROM Config_Loja C INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja WHERE C.Url = %s AND L.Status = 1"
                cursor.execute(sql_loja, (identificador,))
            
            loja_result = cursor.fetchone()
            if not loja_result:
                return RedirectResponse(url="/", status_code=303)
            
            loja_id = loja_result["Id_Loja"]

            # 2. Validar se o produto existe e pertence à loja
            sql_produto = "SELECT Id_Produto, Qtd_Estoque FROM Produto WHERE Id_Produto = %s AND fk_Loja_Id_Loja = %s AND Status = 1"
            cursor.execute(sql_produto, (id_produto, loja_id))
            produto = cursor.fetchone()

            if not produto or produto["Qtd_Estoque"] <= 0:
                return RedirectResponse(url=f"/loja/{identificador}/produto/{id_produto}", status_code=303)

            # 3. Validar quantidade
            if quantidade <= 0 or quantidade > produto["Qtd_Estoque"]:
                quantidade = 1

            # 4. Buscar ou criar carrinho
            sql_carrinho_existe = "SELECT Id_Carrinho FROM Carrinho WHERE fk_Usuario_Id_Usuario = %s AND fk_Loja_Id_Loja = %s"
            cursor.execute(sql_carrinho_existe, (user_id, loja_id))
            carrinho_existe = cursor.fetchone()

            if carrinho_existe:
                carrinho_id = carrinho_existe["Id_Carrinho"]
            else:
                # Criar novo carrinho
                sql_criar_carrinho = "INSERT INTO Carrinho (fk_Usuario_Id_Usuario, fk_Loja_Id_Loja) VALUES (%s, %s)"
                cursor.execute(sql_criar_carrinho, (user_id, loja_id))
                db.commit()
                carrinho_id = cursor.lastrowid

            # 5. Verificar se o produto já está no carrinho
            sql_item_existe = "SELECT Qtd_Produto FROM Carrinho_Produto WHERE fk_Carrinho_Id_Carrinho = %s AND fk_Produto_Id_Produto = %s"
            cursor.execute(sql_item_existe, (carrinho_id, id_produto))
            item_existe = cursor.fetchone()

            if item_existe:
                # Atualizar quantidade (soma com a quantidade anterior)
                nova_qtd = item_existe["Qtd_Produto"] + quantidade
                # Não pode ultrapassar o estoque
                if nova_qtd > produto["Qtd_Estoque"]:
                    nova_qtd = produto["Qtd_Estoque"]
                
                sql_atualizar = "UPDATE Carrinho_Produto SET Qtd_Produto = %s WHERE fk_Carrinho_Id_Carrinho = %s AND fk_Produto_Id_Produto = %s"
                cursor.execute(sql_atualizar, (nova_qtd, carrinho_id, id_produto))
            else:
                # Inserir novo item
                sql_inserir = "INSERT INTO Carrinho_Produto (fk_Carrinho_Id_Carrinho, fk_Produto_Id_Produto, Qtd_Produto) VALUES (%s, %s, %s)"
                cursor.execute(sql_inserir, (carrinho_id, id_produto, quantidade))

            db.commit()

    except Exception as e:
        print(f"ERRO AO ADICIONAR AO CARRINHO: {e}")
        db.rollback()
    finally:
        db.close()

    return RedirectResponse(url=f"/loja/{identificador}/carrinho", status_code=303)


@router.get("/loja/{identificador}/carrinho/aumentar/{id_produto}", response_class=HTMLResponse)
async def aumentar_quantidade(request: Request, identificador: str, id_produto: int, db = Depends(get_db)):
    """Aumenta a quantidade de um produto no carrinho"""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url=f"/loja/{identificador}/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Obter ID da loja
            if identificador.isdigit():
                loja_id = int(identificador)
            else:
                sql_loja = "SELECT L.Id_Loja FROM Config_Loja C INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja WHERE C.Url = %s"
                cursor.execute(sql_loja, (identificador,))
                loja_result = cursor.fetchone()
                loja_id = loja_result["Id_Loja"] if loja_result else None
            
            if not loja_id:
                return RedirectResponse(url=f"/loja/{identificador}/carrinho", status_code=303)

            # Validar se quantidade não ultrapassa estoque
            sql_validacao = """
                SELECT cp.fk_Carrinho_Id_Carrinho, cp.Qtd_Produto, p.Qtd_Estoque
                FROM Carrinho_Produto cp
                INNER JOIN Carrinho c ON cp.fk_Carrinho_Id_Carrinho = c.Id_Carrinho
                INNER JOIN Produto p ON cp.fk_Produto_Id_Produto = p.Id_Produto
                WHERE c.fk_Usuario_Id_Usuario = %s AND c.fk_Loja_Id_Loja = %s AND cp.fk_Produto_Id_Produto = %s
            """
            cursor.execute(sql_validacao, (user_id, loja_id, id_produto))
            res = cursor.fetchone()

            if res and res["Qtd_Produto"] < res["Qtd_Estoque"]:
                cursor.execute("""
                    UPDATE Carrinho_Produto 
                    SET Qtd_Produto = Qtd_Produto + 1 
                    WHERE fk_Carrinho_Id_Carrinho = %s AND fk_Produto_Id_Produto = %s
                """, (res["fk_Carrinho_Id_Carrinho"], id_produto))
                db.commit()
    except Exception as e:
        print(f"ERRO AO AUMENTAR QUANTIDADE: {e}")
        db.rollback()
    finally:
        db.close()

    return RedirectResponse(url=f"/loja/{identificador}/carrinho", status_code=303)


@router.get("/loja/{identificador}/carrinho/diminuir/{id_produto}", response_class=HTMLResponse)
async def diminuir_quantidade(request: Request, identificador: str, id_produto: int, db = Depends(get_db)):
    """Diminui a quantidade de um produto no carrinho"""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url=f"/loja/{identificador}/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Obter ID da loja
            if identificador.isdigit():
                loja_id = int(identificador)
            else:
                sql_loja = "SELECT L.Id_Loja FROM Config_Loja C INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja WHERE C.Url = %s"
                cursor.execute(sql_loja, (identificador,))
                loja_result = cursor.fetchone()
                loja_id = loja_result["Id_Loja"] if loja_result else None
            
            if not loja_id:
                return RedirectResponse(url=f"/loja/{identificador}/carrinho", status_code=303)

            # Garante quantidade mínima de 1
            sql_check = """
                SELECT cp.fk_Carrinho_Id_Carrinho, cp.Qtd_Produto
                FROM Carrinho_Produto cp
                INNER JOIN Carrinho c ON cp.fk_Carrinho_Id_Carrinho = c.Id_Carrinho
                WHERE c.fk_Usuario_Id_Usuario = %s AND c.fk_Loja_Id_Loja = %s AND cp.fk_Produto_Id_Produto = %s
            """
            cursor.execute(sql_check, (user_id, loja_id, id_produto))
            res = cursor.fetchone()

            if res and res["Qtd_Produto"] > 1:
                cursor.execute("""
                    UPDATE Carrinho_Produto 
                    SET Qtd_Produto = Qtd_Produto - 1 
                    WHERE fk_Carrinho_Id_Carrinho = %s AND fk_Produto_Id_Produto = %s
                """, (res["fk_Carrinho_Id_Carrinho"], id_produto))
                db.commit()
    except Exception as e:
        print(f"ERRO AO DIMINUIR QUANTIDADE: {e}")
        db.rollback()
    finally:
        db.close()

    return RedirectResponse(url=f"/loja/{identificador}/carrinho", status_code=303)


@router.get("/loja/{identificador}/carrinho/remover/{id_produto}", response_class=HTMLResponse)
async def remover_produto(request: Request, identificador: str, id_produto: int, db = Depends(get_db)):
    """Remove um produto do carrinho"""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url=f"/loja/{identificador}/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Obter ID da loja
            if identificador.isdigit():
                loja_id = int(identificador)
            else:
                sql_loja = "SELECT L.Id_Loja FROM Config_Loja C INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja WHERE C.Url = %s"
                cursor.execute(sql_loja, (identificador,))
                loja_result = cursor.fetchone()
                loja_id = loja_result["Id_Loja"] if loja_result else None
            
            if not loja_id:
                return RedirectResponse(url=f"/loja/{identificador}/carrinho", status_code=303)

            sql_find = """
                SELECT cp.fk_Carrinho_Id_Carrinho
                FROM Carrinho_Produto cp
                INNER JOIN Carrinho c ON cp.fk_Carrinho_Id_Carrinho = c.Id_Carrinho
                WHERE c.fk_Usuario_Id_Usuario = %s AND c.fk_Loja_Id_Loja = %s AND cp.fk_Produto_Id_Produto = %s
            """
            cursor.execute(sql_find, (user_id, loja_id, id_produto))
            res = cursor.fetchone()

            if res:
                cursor.execute("""
                    DELETE FROM Carrinho_Produto 
                    WHERE fk_Carrinho_Id_Carrinho = %s AND fk_Produto_Id_Produto = %s
                """, (res["fk_Carrinho_Id_Carrinho"], id_produto))
                db.commit()
    except Exception as e:
        print(f"ERRO AO REMOVER PRODUTO: {e}")
        db.rollback()
    finally:
        db.close()

    return RedirectResponse(url=f"/loja/{identificador}/carrinho", status_code=303)

@router.post("/loja/{identificador}/finalizar_compra", response_class=HTMLResponse)
async def finalizar_compra(
    request: Request,
    identificador: str,
    endereco_selecionado: str = Form(...),
    metodo_pagamento: str = Form(...),
    # Campos do novo endereço
    novo_cep: Optional[str] = Form(None),
    nova_cidade: Optional[str] = Form(None),
    nova_rua: Optional[str] = Form(None),
    novo_numero: Optional[str] = Form(None),
    novo_bairro: Optional[str] = Form(None),
    novo_complemento: Optional[str] = Form(None),
    # Campos do cartão
    cc_numero: Optional[str] = Form(None),
    cc_nome: Optional[str] = Form(None),
    cc_validade: Optional[str] = Form(None),
    cc_cvv: Optional[str] = Form(None),
    db = Depends(get_db)
):
    """Processa o checkout e salva a compra no banco"""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url=f"/loja/{identificador}/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Identificar a Loja
            if identificador.isdigit():
                cursor.execute("SELECT Id_Loja FROM Loja WHERE Id_Loja = %s AND Status = 1", (int(identificador),))
            else:
                cursor.execute("SELECT L.Id_Loja FROM Config_Loja C INNER JOIN Loja L ON C.fk_Loja_Id_Loja = L.Id_Loja WHERE C.Url = %s", (identificador,))
            
            loja_result = cursor.fetchone()
            if not loja_result:
                return RedirectResponse(url="/", status_code=303)
            
            loja_id = loja_result["Id_Loja"]

            # 2. Lidar com o Endereço
            id_endereco_final = None

            if endereco_selecionado == "novo":
                # Converte o número de string para int de forma segura
                numero_formatado = int(novo_numero) if novo_numero and novo_numero.isdigit() else 0

                # Inserir novo endereço no banco
                sql_novo_end = """
                    INSERT INTO Endereco (fk_Usuario_Id_Usuario, fk_Loja_Id_Loja, Cep, Rua, Numero, Cidade, Bairro, Complemento, Status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
                """
                # Repare que agora enviamos a variável 'numero_formatado' no execute
                cursor.execute(sql_novo_end, (user_id, loja_id, novo_cep, nova_rua, numero_formatado, nova_cidade, novo_bairro, novo_complemento))
                db.commit()
                id_endereco_final = cursor.lastrowid
            else:
                # Usa o ID do endereço existente selecionado
                id_endereco_final = int(endereco_selecionado)

            # 3. Registrar a Compra no Log_Compra
            sql_log_compra = """
                INSERT INTO Log_Compra (fk_Usuario_Id_Usuario, fk_Loja_Id_Loja, Dat_Compra, fk_Endereco_Id_Endereco, Status)
                VALUES (%s, %s, current_date(), %s, 1)
            """
            cursor.execute(sql_log_compra, (user_id, loja_id, id_endereco_final))
            db.commit()
            id_compra = cursor.lastrowid

            # 4. Pegar os itens do carrinho atual e transferir para Log_Compra_Produto
            sql_carrinho = "SELECT Id_Carrinho FROM Carrinho WHERE fk_Usuario_Id_Usuario = %s AND fk_Loja_Id_Loja = %s ORDER BY Id_Carrinho DESC LIMIT 1"
            cursor.execute(sql_carrinho, (user_id, loja_id))
            carrinho = cursor.fetchone()

            if carrinho:
                carrinho_id = carrinho["Id_Carrinho"]
                
                # Buscar produtos
                cursor.execute("SELECT fk_Produto_Id_Produto, Qtd_Produto FROM Carrinho_Produto WHERE fk_Carrinho_Id_Carrinho = %s", (carrinho_id,))
                itens = cursor.fetchall()

                # Inserir no log de compras
                for item in itens:
                    cursor.execute("""
                        INSERT INTO Log_Compra_Produto (fk_Produto_Id_Produto, fk_Log_Compra_Id_Log_Compras, Qtd_Produto) 
                        VALUES (%s, %s, %s)
                    """, (item["fk_Produto_Id_Produto"], id_compra, item["Qtd_Produto"]))
                    
                    # Abater estoque do Produto
                    cursor.execute("UPDATE Produto SET Qtd_Estoque = COALESCE(Qtd_Estoque, 0) - %s, Qtd_Vendida = COALESCE(Qtd_Vendida, 0) + %s WHERE Id_Produto = %s", (item["Qtd_Produto"], item["Qtd_Produto"], item["fk_Produto_Id_Produto"]))

                # 5. Limpar o carrinho (apaga os registros da tabela associativa)
                cursor.execute("DELETE FROM Carrinho_Produto WHERE fk_Carrinho_Id_Carrinho = %s", (carrinho_id,))
                db.commit()

    except Exception as e:
        print(f"ERRO AO FINALIZAR COMPRA: {e}")
        db.rollback()
        return RedirectResponse(url=f"/loja/{identificador}/carrinho?erro=finalizar", status_code=303)
    finally:
        db.close()

    # Redireciona para a home da loja (ou para uma página de sucesso, se você criar uma)
    return RedirectResponse(url=f"/loja/{identificador}/home?sucesso=compra", status_code=303)

@router.get("/loja/{identificador}/historico", response_class=HTMLResponse)
async def historico_compras_loja(
    request: Request,
    identificador: str,
    db = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url=f"/loja/{identificador}/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            if identificador.isdigit():
                sql_loja = """
                    SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url
                    FROM Loja L
                    LEFT JOIN Config_Loja C 
                        ON C.fk_Loja_Id_Loja = L.Id_Loja
                    WHERE L.Id_Loja = %s
                    AND L.Status = 1
                """
                cursor.execute(sql_loja, (int(identificador),))
            else:
                sql_loja = """
                    SELECT L.*, C.Cor_Principal, C.Cor_Secundaria, C.Logo, C.Banner, C.Url
                    FROM Config_Loja C
                    INNER JOIN Loja L 
                        ON C.fk_Loja_Id_Loja = L.Id_Loja
                    WHERE C.Url = %s
                    AND L.Status = 1
                """
                cursor.execute(sql_loja, (identificador,))

            loja = cursor.fetchone()

            if not loja:
                return RedirectResponse(url="/", status_code=303)

            if loja.get("Logo"):
                loja["Logo_B64"] = base64.b64encode(loja["Logo"]).decode("utf-8")

            sql = """
                SELECT
                    LC.Id_Log_Compras,
                    LC.Dat_Compra,
                    LC.Status,
                    P.Id_Produto,
                    P.Nome AS Nome_Produto,
                    P.Preco,
                    LCP.Qtd_Produto,
                    (P.Preco * LCP.Qtd_Produto) AS Total_Produto,
                    (
                        SELECT Imagem
                        FROM Imagem_Produto
                        WHERE fk_Produto_Id_Produto = P.Id_Produto
                        LIMIT 1
                    ) AS Imagem

                FROM Log_Compra LC

                INNER JOIN Log_Compra_Produto LCP
                    ON LCP.fk_Log_Compra_Id_Log_Compras = LC.Id_Log_Compras

                INNER JOIN Produto P
                    ON P.Id_Produto = LCP.fk_Produto_Id_Produto

                WHERE LC.fk_Usuario_Id_Usuario = %s
                AND LC.fk_Loja_Id_Loja = %s

                ORDER BY LC.Dat_Compra DESC, LC.Id_Log_Compras DESC
            """

            cursor.execute(sql, (user_id, loja["Id_Loja"]))
            compras_raw = cursor.fetchall()

            compras_agrupadas = {}

            for compra in compras_raw:
                id_compra = compra["Id_Log_Compras"]

                if id_compra not in compras_agrupadas:
                    compras_agrupadas[id_compra] = {
                        "Id_Log_Compras": id_compra,
                        "Dat_Compra": compra["Dat_Compra"],
                        "Status": compra["Status"],
                        "Total_Pedido": 0,
                        "Produtos": []
                    }

                imagem_b64 = None
                if compra.get("Imagem"):
                    imagem_b64 = base64.b64encode(compra["Imagem"]).decode("utf-8")

                compras_agrupadas[id_compra]["Produtos"].append({
                    "Id_Produto": compra["Id_Produto"],
                    "Nome_Produto": compra["Nome_Produto"],
                    "Preco": compra["Preco"],
                    "Qtd_Produto": compra["Qtd_Produto"],
                    "Total_Produto": compra["Total_Produto"],
                    "Imagem_B64": imagem_b64
                })

                compras_agrupadas[id_compra]["Total_Pedido"] += compra["Total_Produto"]

            compras = list(compras_agrupadas.values())

    except Exception as e:
        print(f"ERRO AO CARREGAR HISTÓRICO DE COMPRAS: {e}")
        compras = []
        loja = None

    finally:
        db.close()

    return templates.TemplateResponse("loja/historicoCompras.html", {
        "request": request,
        "loja": loja,
        "compras": compras,
        "identificador": identificador,
        "categorias_selecionadas": [],
        "busca_atual": None,
        "preco_selecionado": None,
        "obterAvatarUsuario": obterAvatarUsuario
    })