import pymysql
import base64
import auth

from typing import List
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from database import get_db
from templates import templates

router = APIRouter()

@router.get("/GerenciarProdutos", response_class=HTMLResponse)
async def gerenciar_produtos(
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
        sql = """
            SELECT P.*,
            (SELECT Imagem FROM Imagem_Produto WHERE fk_Produto_Id_Produto = P.Id_Produto LIMIT 1) as Imagem
            FROM Produto P WHERE fk_Loja_Id_Loja = %s AND Status = 1
        """
        cursor.execute(sql, (id_loja,))
        produtos = cursor.fetchall()

        cursor.execute("SELECT * FROM Categoria WHERE fk_Loja_Id_Loja = %s AND Status = 1", (id_loja,))
        categorias = cursor.fetchall()

        for p in produtos:
            if p["Imagem"]:
                p["Imagem_base64"] = base64.b64encode(p["Imagem"]).decode('utf-8')

    return templates.TemplateResponse("gerencProdutos/gerenciarProdutos.html", {
        "request": request,
        "produtos": produtos,
        "categorias": categorias,
        "id_loja": id_loja
    })


@router.get("/FormProduto", response_class=HTMLResponse)
async def form_produto(
    request: Request,
    id_loja: int,
    id: int = None,
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)

    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, id_loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    produto = None
    imagens_prod = []
    categorias_todas = []
    categorias_vinculadas = []

    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM Categoria WHERE fk_Loja_Id_Loja = %s AND Status = 1", (id_loja,))
        categorias_todas = cursor.fetchall()

        if id:
            cursor.execute("SELECT * FROM Produto WHERE Id_Produto = %s AND Status = 1", (id,))
            produto = cursor.fetchone()

            cursor.execute("SELECT Id_Imagem, Imagem FROM Imagem_Produto WHERE fk_Produto_Id_Produto = %s", (id,))
            rows = cursor.fetchall()

            for r in rows:
                imagens_prod.append({
                    "id": r["Id_Imagem"],
                    "base64": base64.b64encode(r["Imagem"]).decode('utf-8')
                })

            cursor.execute("SELECT fk_Categoria_Id_Categoria FROM Produto_Categoria WHERE fk_Produto_Id_Produto = %s", (id,))
            categorias_vinculadas = [c["fk_Categoria_Id_Categoria"] for c in cursor.fetchall()]

    return templates.TemplateResponse("gerencProdutos/formProduto.html", {
        "request": request,
        "produto": produto,
        "imagens": imagens_prod,
        "categorias": categorias_todas,
        "categorias_vinculadas": categorias_vinculadas,
        "id_loja": id_loja
    })


@router.post("/SalvarProduto")
async def salvar_produto(
    request: Request,
    id_loja: int = Form(...),
    Id_Produto: str = Form(None),
    Nome: str = Form(...),
    Preco: float = Form(...),
    Qtd_Estoque: int = Form(...),
    Categorias: List[int] = Form(default=[]),
    Descricao: str = Form(None),
    Imagens: List[UploadFile] = File(None),
    ImagensParaDeletar: List[int] = Form(default=[]),
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)

    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, id_loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    try:
        with db.cursor() as cursor:

            if Id_Produto:
                sql = "UPDATE Produto SET Nome=%s, Preco=%s, Qtd_Estoque=%s, Descricao=%s WHERE Id_Produto=%s"
                cursor.execute(sql, (Nome, Preco, Qtd_Estoque, Descricao, Id_Produto))
                id_final = Id_Produto
            else:
                sql = "INSERT INTO Produto (fk_Loja_Id_Loja, Nome, Preco, Qtd_Estoque, Descricao, Status) VALUES (%s, %s, %s, %s, %s, 1)"
                cursor.execute(sql, (id_loja, Nome, Preco, Qtd_Estoque, Descricao))
                id_final = cursor.lastrowid

            cursor.execute("DELETE FROM Produto_Categoria WHERE fk_Produto_Id_Produto = %s", (id_final,))
            for cat_id in Categorias:
                cursor.execute("INSERT INTO Produto_Categoria (fk_Categoria_Id_Categoria, fk_Produto_Id_Produto, Status) VALUES (%s, %s, 1)", (cat_id, id_final))

            for img_id in ImagensParaDeletar:
                cursor.execute("DELETE FROM Imagem_Produto WHERE Id_Imagem = %s", (img_id,))

            for img in Imagens:
                if img.filename:
                    content = await img.read()
                    cursor.execute("INSERT INTO Imagem_Produto (fk_Produto_Id_Produto, Imagem) VALUES (%s, %s)", (id_final, content))

            db.commit()
        return RedirectResponse(url=f"/GerenciarProdutos?id_loja={id_loja}", status_code=303)
    finally:
        db.close()


@router.get("/DeletarProduto/{id}")
async def deletar_produto(
    request: Request,
    id: int,
    id_loja: int,
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)

    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, id_loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("UPDATE Produto SET Status = 0 WHERE Id_Produto = %s", (id,))
        db.commit()

    return RedirectResponse(url=f"/GerenciarProdutos?id_loja={id_loja}", status_code=303)

@router.post("/AlterarEstoqueProduto")
async def alterar_estoque_produto(
    request: Request,
    id_produto: int = Form(...),
    qtd_alterar: int = Form(...),
    id_loja: int = Form(...),
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)

    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, id_loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    with db.cursor(pymysql.cursors.DictCursor) as cursor:

        cursor.execute("SELECT Qtd_Estoque FROM Produto WHERE Id_Produto = %s AND fk_Loja_Id_Loja = %s AND Status = 1", (id_produto, id_loja))

        QtdAtual = cursor.fetchone()

        if QtdAtual['Qtd_Estoque'] < 0:
            return RedirectResponse(url=f"/GerenciarProdutos?id_loja={id_loja}", status_code=303)
        elif QtdAtual['Qtd_Estoque'] + qtd_alterar < 0:
            return RedirectResponse(url=f"/GerenciarProdutos?id_loja={id_loja}", status_code=303)

        cursor.execute("UPDATE Produto SET Qtd_Estoque = %s WHERE Id_Produto = %s", (QtdAtual['Qtd_Estoque'] + qtd_alterar, id_produto))

        db.commit()

    return RedirectResponse(url=f"/GerenciarProdutos?id_loja={id_loja}", status_code=303)

#CRUD de categoria

@router.get("/GerenciarCategorias", response_class=HTMLResponse)
async def gerenciar_categorias(
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

        cursor.execute("""
            SELECT *
            FROM Categoria
            WHERE fk_Loja_Id_Loja = %s
            AND Status = 1
            ORDER BY Nome
        """, (id_loja,))

        categorias = cursor.fetchall()

    return templates.TemplateResponse(
        "gerencCategoria/gerenciarCategoria.html",
        {
            "request": request,
            "categorias": categorias,
            "id_loja": id_loja,
            "sidebar_active": "categoria"
        }
    )

@router.get("/FormCategoria", response_class=HTMLResponse)
async def form_categoria(
    request: Request,
    id_loja: int,
    id: int = None,
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)

    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, id_loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    categoria = None

    with db.cursor(pymysql.cursors.DictCursor) as cursor:

        if id:
            cursor.execute("""
                SELECT *
                FROM Categoria
                WHERE Id_Categoria = %s
                AND fk_Loja_Id_Loja = %s
                AND Status = 1
            """, (id, id_loja))

            categoria = cursor.fetchone()

    return templates.TemplateResponse(
        "gerencCategoria/formCategoria.html",
        {
            "request": request,
            "categoria": categoria,
            "id_loja": id_loja
        }
    )

@router.post("/SalvarCategoria")
async def salvar_categoria(
    request: Request,
    id_loja: int = Form(...),
    Id_Categoria: str = Form(None),
    Nome: str = Form(...),
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)

    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, id_loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    try:
        with db.cursor() as cursor:

            if Id_Categoria:
                cursor.execute("UPDATE Categoria SET Nome=%s WHERE Id_Categoria=%s AND fk_Loja_Id_Loja=%s",
                               (Nome, Id_Categoria, id_loja))
            else:
                cursor.execute("INSERT INTO Categoria (fk_Loja_Id_Loja, Nome, Status) VALUES (%s, %s, 1)",
                               (id_loja, Nome))

            db.commit()

        return RedirectResponse(url=f"/GerenciarCategorias?id_loja={id_loja}", status_code=303)

    finally:
        db.close()


@router.get("/DeletarCategoria/{id}")
async def deletar_categoria(
    request: Request,
    id: int,
    id_loja: int,
    db = Depends(get_db)
):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/login", status_code=303)

    user_id = request.session.get("user_id")

    if not await auth.verificarUsuarioPerfil(db, user_id, 2, id_loja):
        return RedirectResponse(url="/perfilLojista", status_code=303)

    with db.cursor() as cursor:
        cursor.execute("DELETE FROM Categoria WHERE Id_Categoria = %s AND fk_Loja_Id_Loja = %s",
                       (id, id_loja))
        db.commit()

    return RedirectResponse(url=f"/GerenciarCategorias?id_loja={id_loja}", status_code=303)
