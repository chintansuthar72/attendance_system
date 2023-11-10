# Celery Configuration file 
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

app = Celery('attendance_system')

# Time zone
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')

# Using Redis as the message broker
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat Settings
app.conf.beat_schedule = {
    'fetch-attendance-data': {
        'task': 'attendance_data.tasks.fetch_attendance_data',
        'schedule': crontab(hour=15, minute=12),
    },
    'send-notification-mails' : {
        'task' : 'send_notification.tasks.send_mails',
        'schedule' : crontab(hour=5,minute=0),
    }
}

app.autodiscover_tasks()

# Debug
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')