import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    'reset-weekly-topusers-every-sunday-night': {
        'task': 'app.bot.tasks.reset_weekly_earned_and_send_report',
        'schedule': crontab(hour=23, minute=59, day_of_week=6),  # har yakshanba, 23:59 da
    },
}