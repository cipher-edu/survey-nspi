# external_auth_project/celery.py
import os
from celery import Celery

# Django settings modulini Celery uchun standart sifatida o'rnatish.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'external_auth_project.settings')

app = Celery('external_auth_project')

# Bu yerda Celery sozlamalarini Django settings.py faylidan oladi,
# 'CELERY_' prefiksi bilan.
app.config_from_object('django.conf:settings', namespace='CELERY')

# INSTALLED_APPS dagi barcha task modullarini avtomatik topish.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')