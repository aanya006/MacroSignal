import os
from app import create_app
from app.models.db import init_db, execute_query, get_connection, release_connection
from app.services.scheduler import init_scheduler

app = create_app()
init_db()

# Seed pre-classified data if DB is empty
def seed_if_empty():
    try:
        result = execute_query("SELECT COUNT(*) as count FROM themes")
        if result and result[0]['count'] == 0:
            seed_path = os.path.join(os.path.dirname(__file__), 'seed_data.sql')
            if os.path.exists(seed_path):
                conn = get_connection()
                try:
                    with conn.cursor() as cur:
                        with open(seed_path, 'r') as f:
                            cur.execute(f.read())
                    conn.commit()
                    print("Seeded database with pre-classified data")
                except Exception as e:
                    conn.rollback()
                    print(f"Seed error: {e}")
                finally:
                    release_connection(conn)
    except Exception as e:
        print(f"Seed check error: {e}")

seed_if_empty()

init_scheduler(app)
