from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from application.views import async_task

def start():
    scedular = BackgroundScheduler()
    scedular.add_job(async_task,'interval',minutes=30)
    scedular.start()