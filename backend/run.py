import os
from app import create_app
from app.models.db import init_db

app = create_app()

if __name__ == '__main__':
    init_db()

    # Start scheduler only in the main process (not the reloader)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        from app.services.scheduler import init_scheduler
        init_scheduler(app)

    app.run(debug=True, port=5001)
