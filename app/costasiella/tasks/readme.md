# RabbitMQ server

sudo apt-get install rabbitmq-server

# Define tasks

costasiella/tasks.py

# Schedule taks

Django Admin

# Scheduler (Beat)

```bash
celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

# Check that messages from beat arrive in queue

```bash
sudo rabbitmqctl list_queues
```

# Celery Worker

```bash
celery -A app worker -l info
```

# View results:

query database:
select * from django_celery_results_taskresult;

# test tasks from shell

`./manage.py shell`

```python
from costasiella.tasks import add
task = add.delay(2, 5)
task.get()
7
```
