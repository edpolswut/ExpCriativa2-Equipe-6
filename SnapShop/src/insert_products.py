import pymysql

# Configuração do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "abc123",
    "database": "SnapShop"
}

def insert_sample_products():
    db = pymysql.connect(**DB_CONFIG)
    try:
        with db.cursor() as cursor:
            # Insert 3 sample products
            products = [
                {
                    "fk_Loja_Id_Loja": 1,
                    "Nome": "Boneco de Ação Super Herói",
                    "Preco": 49.99,
                    "Qtd_Estoque": 100,
                    "Status": 1,
                    "Imagem": b'dummy image data for super hero'  # Dummy BLOB data
                },
                {
                    "fk_Loja_Id_Loja": 1,
                    "Nome": "Carrinho de Corrida Vermelho",
                    "Preco": 29.99,
                    "Qtd_Estoque": 150,
                    "Status": 1,
                    "Imagem": b'dummy image data for red car'  # Dummy BLOB data
                },
                {
                    "fk_Loja_Id_Loja": 1,
                    "Nome": "Quebra-Cabeça 500 Peças",
                    "Preco": 39.99,
                    "Qtd_Estoque": 80,
                    "Status": 1,
                    "Imagem": b'dummy image data for puzzle'  # Dummy BLOB data
                }
            ]

            for prod in products:
                # Insert into Produto
                sql_prod = """
                    INSERT INTO Produto (fk_Loja_Id_Loja, Nome, Preco, Qtd_Estoque, Status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_prod, (prod["fk_Loja_Id_Loja"], prod["Nome"], prod["Preco"], prod["Qtd_Estoque"], prod["Status"]))
                prod_id = cursor.lastrowid

                # Insert into Imagem_Produto
                sql_img = """
                    INSERT INTO Imagem_Produto (fk_Produto_Id_Produto, Imagem)
                    VALUES (%s, %s)
                """
                cursor.execute(sql_img, (prod_id, prod["Imagem"]))

            db.commit()
            print("3 sample products inserted successfully!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_sample_products()