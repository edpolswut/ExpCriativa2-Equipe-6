# Este arquivo será responsável por lidar com a autorização de usuários.

import pymysql
from fastapi import Depends

from database import get_db

async def verificarUsuarioPerfil(CodUsuario: int, CodPerfil: int, CodLoja: int = None, db = Depends(get_db)):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        if CodLoja:
            cursor.execute("""SELECT 1 
                                FROM Usuario_perfil 
                               WHERE fk_Usuario_Id_Usuario = %i
                                 AND fk_Perfil_Id_Perfil = %i
                                 AND fk_Loja_Id_Loja = %i""", (CodUsuario, CodPerfil, CodLoja))
        else:
            cursor.execute("""SELECT 1 
                                FROM Usuario_perfil 
                               WHERE fk_Usuario_Id_Usuario = %i
                                 AND fk_Perfil_Id_Perfil = %i""", (CodUsuario, CodPerfil))

        if cursor.fetchone():
            return True
    return False
