from dotenv import load_dotenv
import os
import psycopg2


load_dotenv()
token = os.getenv('TOKEN')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')


if __name__ == '__main__':
    import psycopg2

    conn = psycopg2.connect("""
        host=rc1b-3tkrcdsospburzw7.mdb.yandexcloud.net
        port=6432
        dbname=db1
        user=user1
        password=Lyapin8915 
        target_session_attrs=read-write
    """)

    q = conn.cursor()
    q.execute('SELECT version()')

    print(q.fetchone())

    conn.close()
    print(DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)