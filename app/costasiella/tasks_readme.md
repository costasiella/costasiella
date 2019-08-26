# Define tasks
costasiella/tasks.py

# Schedule taks
Django Admin

# Scheduler (Beat)
celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Check that messages from beat arrive in queue
sudo rabbitmqctl list_queues

# Worker
celery -A app worker -l info

# View results:
query database:
select * from django_celery_results_taskresult;



# test tasks from shell
./manage.py shell
>>> from costasiella.tasks import add
>>> task = add.delay(2, 5)
>>> task.get()
7
