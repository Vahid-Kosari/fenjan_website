from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capstone.settings")

app = Celery("capstone")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Determine the capstone directory
capstone_dir = os.path.dirname(os.path.abspath(__file__))
celerybeat_schedule_dir_path = os.path.join(capstone_dir, "celerybeat-schedule")

# Ensure the directory exists
if not os.path.exists(celerybeat_schedule_dir_path):
    os.makedirs(celerybeat_schedule_dir_path)

app.conf.beat_schedule_filename = os.path.join(
    celerybeat_schedule_dir_path, "celerybeat-schedule"
)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
