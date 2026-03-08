import psycopg2
from psycopg2 import pool
from app.utils.config import DATABASE_URL

_connection_pool = None


def get_pool():
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)
    return _connection_pool


def get_connection():
    return get_pool().getconn()


def release_connection(conn):
    get_pool().putconn(conn)


def execute_query(query, params=None, fetch=True):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)


def execute_many(query, params_list):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for params in params_list:
                cur.execute(query, params)
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)


def init_db():
    import os
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'schema.sql')
    if not os.path.exists(schema_path):
        print(f"schema.sql not found at {schema_path}")
        return
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            with open(schema_path, 'r') as f:
                cur.execute(f.read())
            conn.commit()
            print("Database schema initialized successfully")
    except Exception as e:
        conn.rollback()
        print(f"Schema initialization error: {e}")
    finally:
        release_connection(conn)
