from app import create_app
from app.models.db import init_db
from app.services.scheduler import init_scheduler

app = create_app()
init_db()
init_scheduler(app)
