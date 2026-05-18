import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Familia@1",
    "database": "SnapShop"
}

def get_db():
    return pymysql.connect(**DB_CONFIG)