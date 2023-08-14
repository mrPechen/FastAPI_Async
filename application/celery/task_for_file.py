from celery import Celery
from application.db_app.settings import settings

print(f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@{settings.RABBITMQ_HOST}:{settings.REDIS_PORT}//")

task = Celery('task_for_file',
              broker=f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//")

task.conf.beat_schedule = {
    'add-every-15-seconds': {
        'task': 'application.admin.tasks.sync_run',
        #'task': '..admin.tasks.sync_run',
        'schedule': 15.0,
    },
}
task.conf.timezone = 'UTC'
task.autodiscover_tasks()
