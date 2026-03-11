from app import create_app
from app.services.scheduler import init_scheduler

app = create_app()

init_scheduler(app)
