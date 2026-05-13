import pymysql
import base64
from fastapi.templating import Jinja2Templates
from database import get_db

templates = Jinja2Templates(directory="front/templates")

def obterAvatarUsuario(user_id: int):
    db = get_db()
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT Imagem_Usuario FROM Usuario WHERE Id_Usuario = %s", (user_id,))
            resultado = cursor.fetchone()
            if resultado and resultado["Imagem_Usuario"]:
                return base64.b64encode(resultado["Imagem_Usuario"]).decode('utf-8')
    except Exception as e:
        print(f"Erro ao buscar avatar: {e}")
    finally:
        db.close()
    return None

templates.env.globals["obterAvatarUsuario"] = obterAvatarUsuario