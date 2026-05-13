import pymysql
import base64
import auth

from typing import List, Optional
from fastapi import APIRouter, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from database import get_db
from templates import templates

router = APIRouter()

@router.get("/loja/{identificador}", name="vitrine_loja", response_class=HTMLResponse)
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

    return templates.TemplateResponse("mainpage.html", {
        "request": request, 
        "loja": loja,
        "produtos": produtos,
        "categorias_loja": categorias_loja,
        "busca_atual": busca,
        "categorias_selecionadas": categorias or [],
        "preco_selecionado": preco
    })

@router.get("/produto/{id_produto}")
async def detalhes_produto(request: Request, id_produto: int, db = Depends(get_db)):
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
            WHERE L.Id_Loja = %s
        """
        cursor.execute(sql_loja, (produto["fk_Loja_Id_Loja"],))
        loja = cursor.fetchone()
        
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

    return templates.TemplateResponse("visualizacao.html", {
        "request": request, 
        "produto": produto,
        "loja": loja
    })