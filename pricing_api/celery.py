# pricing_api/celery.py

import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pricing_api.settings')

app = Celery('pricing_api')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 🔥 Auto-discover tasks.py files in all installed apps
app.autodiscover_tasks()
