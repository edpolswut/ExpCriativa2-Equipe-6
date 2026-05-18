import pymysql
import base64
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

# Importando a conexão com o banco e a configuração de templates do seu projeto
from database import get_db
from templates import templates

router = APIRouter()


@router.get("/carrinho", response_class=HTMLResponse)
async def exibir_carrinho(request: Request, db = Depends(get_db)):
    # Verifica se o usuário está logado
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    loja = None
    itens_carrinho = []
    total_produtos = 0.0

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Busca o carrinho ativo mais recente do usuário e os dados da loja vinculada
            sql_carrinho = """
                SELECT c.Id_Carrinho, l.Id_Loja, l.Nome 
                FROM Carrinho c
                INNER JOIN Loja l ON c.fk_Loja_Id_Loja = l.Id_Loja
                WHERE c.fk_Usuario_Id_Usuario = %s 
                ORDER BY c.Id_Carrinho DESC LIMIT 1
            """
            cursor.execute(sql_carrinho, (user_id,))
            carrinho = cursor.fetchone()

            if carrinho:
                loja = {
                    "Id_Loja": carrinho["Id_Loja"],
                    "Nome": carrinho["Nome"]
                }

                # 2. Busca os itens pertencentes a este carrinho mapeando com Produto e Imagem_Produto
                sql_itens = """
                    SELECT p.Id_Produto, p.Nome, p.Preco, p.Qtd_Estoque, cp.Qtd_Produto,
                    (SELECT ip.Imagem 
                    FROM Imagem_Produto ip  
                    WHERE p.Id_Produto = ip.fk_Produto_Id_Produto AND ROWNUM = 1)
                    FROM Carrinho_Produto cp
                    INNER JOIN Produto p ON cp.fk_Produto_Id_Produto = p.Id_Produto
                    WHERE cp.fk_Carrinho_Id_Carrinho = %s
                """
                cursor.execute(sql_itens, (carrinho["Id_Carrinho"],))
                itens_banco = cursor.fetchall()

                # 3. Processa os itens calculando totais e convertendo o BLOB da imagem para Base64
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

    except Exception as e:
        print(f"ERRO AO CARREGAR CARRINHO: {e}")
    finally:
        db.close()

    # Retorna o template injetando o contexto esperado pelo Jinja2
    return templates.TemplateResponse("loja/carrinho.html", {
        "request": request,
        "loja": loja,
        "itens_carrinho": itens_carrinho,
        "total_produtos": total_produtos,
        "total_compra": total_produtos  # Frete grátis adicionado no layout visual
    })


@router.get("/carrinho/aumentar/{id_produto}")
async def aumentar_quantidade(request: Request, id_produto: int, db = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Seleciona o item para validar se a quantidade desejada não supera o estoque disponível
            sql_validacao = """
                SELECT cp.fk_Carrinho_Id_Carrinho, cp.Qtd_Produto, p.Qtd_Estoque
                FROM Carrinho_Produto cp
                INNER JOIN Carrinho c ON cp.fk_Carrinho_Id_Carrinho = c.Id_Carrinho
                INNER JOIN Produto p ON cp.fk_Produto_Id_Produto = p.Id_Produto
                WHERE c.fk_Usuario_Id_Usuario = %s AND cp.fk_Produto_Id_Produto = %s
            """
            cursor.execute(sql_validacao, (user_id, id_produto))
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

    return RedirectResponse(url="/carrinho", status_code=303)


@router.get("/carrinho/diminuir/{id_produto}")
async def diminuir_quantidade(request: Request, id_produto: int, db = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Garante que a quantidade mínima permaneça em 1 unidade
            sql_check = """
                SELECT cp.fk_Carrinho_Id_Carrinho, cp.Qtd_Produto
                FROM Carrinho_Produto cp
                INNER JOIN Carrinho c ON cp.fk_Carrinho_Id_Carrinho = c.Id_Carrinho
                WHERE c.fk_Usuario_Id_Usuario = %s AND cp.fk_Produto_Id_Produto = %s
            """
            cursor.execute(sql_check, (user_id, id_produto))
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

    return RedirectResponse(url="/carrinho", status_code=303)


@router.get("/carrinho/remover/{id_produto}")
async def remover_produto(request: Request, id_produto: int, db = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_find = """
                SELECT cp.fk_Carrinho_Id_Carrinho
                FROM Carrinho_Produto cp
                INNER JOIN Carrinho c ON cp.fk_Carrinho_Id_Carrinho = c.Id_Carrinho
                WHERE c.fk_Usuario_Id_Usuario = %s AND cp.fk_Produto_Id_Produto = %s
            """
            cursor.execute(sql_find, (user_id, id_produto))
            res = cursor.fetchone()

            if res:
                # Remove o item da tabela associativa Carrinho_Produto
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

    return RedirectResponse(url="/carrinho", status_code=303)