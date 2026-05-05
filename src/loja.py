import pymysql
import base64
import auth

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import get_db
from templates import templates

router = APIRouter()

@router.get("/loja/{identificador}", name="vitrine_loja", response_class=HTMLResponse)
async def vitrine_loja(request: Request, identificador: str, db = Depends(get_db)):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # 1. Verifica se o identificador é um número (ID) ou texto (URL personalizada)
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

        sql_produtos = """
            SELECT Id_Produto, Nome, Preco, Qtd_Estoque 
            FROM Produto 
            WHERE fk_Loja_Id_Loja = %s AND Status = 1
            ORDER BY Nome
        """
        cursor.execute(sql_produtos, (loja["Id_Loja"],))
        produtos = cursor.fetchall()

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
        "produtos": produtos
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

    return templates.TemplateResponse("loja/visualizacao.html", {
    "request": request, 
    "produto": produto,
    "loja": loja
})
