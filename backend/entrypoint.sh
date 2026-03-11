#!/bin/sh
set -e

# Run migrations once before starting workers
python -c "from app.models.db import init_db; init_db()"

# Seed if empty
python -c "
import os, sys
sys.path.insert(0, '/app')
from app.models.db import execute_query, get_connection, release_connection
try:
    result = execute_query('SELECT COUNT(*) as count FROM themes')
    if result and result[0]['count'] == 0:
        seed_path = os.path.join('/app', 'seed_data.sql')
        if os.path.exists(seed_path):
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    with open(seed_path, 'r') as f:
                        cur.execute(f.read())
                conn.commit()
                print('Seeded database with pre-classified data')
            except Exception as e:
                conn.rollback()
                print(f'Seed error: {e}')
            finally:
                release_connection(conn)
except Exception as e:
    print(f'Seed check error: {e}')
"

# Start gunicorn
exec gunicorn -b 0.0.0.0:5001 --workers 2 --timeout 120 wsgi:app
