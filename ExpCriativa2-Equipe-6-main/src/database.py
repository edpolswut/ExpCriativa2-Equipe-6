import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "PUC@1234",
    "database": "SnapShop"
}

def get_db():
    return pymysql.connect(**DB_CONFIG)