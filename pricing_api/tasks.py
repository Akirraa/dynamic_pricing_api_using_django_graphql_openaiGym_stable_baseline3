from celery import shared_task

@shared_task
def test_celery_task():
    print("Test Celery Task executed successfully!")
    return "Hello from Celery"
