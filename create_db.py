import psycopg2
from config import POSTGRES_PASSWORD

if __name__ == '__main__':
    conn = psycopg2.connect(host='localhost',
                            user='postgres',
                            password=POSTGRES_PASSWORD)

    conn.autocommit = True

    conn.cursor().execute('DROP DATABASE IF EXISTS shop_db')
    conn.cursor().execute('CREATE DATABASE shop_db')
    conn.cursor().close()
    conn.close()