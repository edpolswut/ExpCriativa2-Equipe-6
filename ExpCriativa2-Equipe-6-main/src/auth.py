import pymysql

async def verificarUsuarioPerfil(db, CodUsuario: int, CodPerfil: int, CodLoja: int = None):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        if CodLoja:
            cursor.execute("""SELECT 1 
                                FROM Usuario_perfil 
                               WHERE fk_Usuario_Id_Usuario = %s
                                 AND fk_Perfil_Id_Perfil = %s
                                 AND fk_Loja_Id_Loja = %s""", (CodUsuario, CodPerfil, CodLoja))
        else:
            cursor.execute("""SELECT 1 
                                FROM Usuario_perfil 
                               WHERE fk_Usuario_Id_Usuario = %s
                                 AND fk_Perfil_Id_Perfil = %s""", (CodUsuario, CodPerfil))

        if cursor.fetchone():
            return True
    return False
