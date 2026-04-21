import pymysql
import base64
from typing import List
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_db

templates = Jinja2Templates(directory="front/templates")
router = APIRouter()

@router.get("/GerenciarProdutos", response_class=HTMLResponse)
async def gerenciar_produtos(request: Request, id_loja: int, db = Depends(get_db)):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # Busca produtos APENAS da loja selecionada
        sql = """
            SELECT P.*, 
            (SELECT Imagem FROM Imagem_Produto WHERE fk_Produto_Id_Produto = P.Id_Produto LIMIT 1) as Imagem
            FROM Produto P WHERE fk_Loja_Id_Loja = %s AND Status = 1
        """
        cursor.execute(sql, (id_loja,))
        produtos = cursor.fetchall()
        
        for p in produtos:
            if p["Imagem"]:
                p["Imagem_base64"] = base64.b64encode(p["Imagem"]).decode('utf-8')

    return templates.TemplateResponse(
        request=request,
        name="gerencProdutos/gerenciarProdutos.html",
        context={
            "request": request, 
            "produtos": produtos, 
            "id_loja": id_loja # Passamos o ID para o HTML manter a navegação
        }
    )

@router.get("/FormProduto", response_class=HTMLResponse)
async def form_produto(request: Request, id_loja: int, id: int = None, db = Depends(get_db)):
    produto = None
    imagens_prod = []
    
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # Busca categorias da loja específica
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

    return templates.TemplateResponse(
        request=request,
        name="gerencProdutos/formProduto.html",
        context={
            "request": request, 
            "produto": produto, 
            "imagens": imagens_prod,
            "categorias": categorias_todas,
            "id_loja": id_loja
        }
    )

@router.post("/SalvarProduto")
async def salvar_produto(
    id_loja: int = Form(...), # Agora recebemos do formulário
    Id_Produto: str = Form(None),
    Nome: str = Form(...),
    Preco: float = Form(...),
    Qtd_Estoque: int = Form(...),
    Imagens: List[UploadFile] = File(None),
    db = Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            if Id_Produto:
                sql = "UPDATE Produto SET Nome=%s, Preco=%s, Qtd_Estoque=%s WHERE Id_Produto=%s"
                cursor.execute(sql, (Nome, Preco, Qtd_Estoque, Id_Produto))
                id_final = Id_Produto
            else:
                # Usa o id_loja dinâmico no INSERT
                sql = "INSERT INTO Produto (fk_Loja_Id_Loja, Nome, Preco, Qtd_Estoque, Status) VALUES (%s, %s, %s, %s, 1)"
                cursor.execute(sql, (id_loja, Nome, Preco, Qtd_Estoque))
                id_final = cursor.lastrowid

            for img in Imagens:
                if img.filename:
                    content = await img.read()
                    cursor.execute("INSERT INTO Imagem_Produto (fk_Produto_Id_Produto, Imagem) VALUES (%s, %s)", (id_final, content))
            
            db.commit()
        return RedirectResponse(url=f"/GerenciarProdutos?id_loja={id_loja}", status_code=303)
    finally:
        db.close()

@router.get("/DeletarProduto/{id}")
async def deletar_produto(id: int, db = Depends(get_db)):
    # Primeiro descobrimos de qual loja é o produto para saber para onde voltar
    with db.cursor() as cursor:
        cursor.execute("SELECT fk_Loja_Id_Loja FROM Produto WHERE Id_Produto = %s", (id,))
        id_loja = cursor.fetchone()[0]
        cursor.execute("UPDATE Produto SET Status = 0 WHERE Id_Produto = %s", (id,))
        db.commit()
    return RedirectResponse(url=f"/GerenciarProdutos?id_loja={id_loja}", status_code=303)