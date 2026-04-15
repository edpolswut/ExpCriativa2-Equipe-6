import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "abc123", #lembrar de mudar a senha dependendo do pc que usar pra testar
    "database": "SnapShop"
}

def get_db():
    return pymysql.connect(**DB_CONFIG)