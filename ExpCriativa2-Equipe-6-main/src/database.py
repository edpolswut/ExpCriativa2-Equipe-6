import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "abc123",
    "database": "SnapShop"
}

def get_db():
    return pymysql.connect(**DB_CONFIG)