# Generated by Django 3.1.13 on 2021-12-17 10:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0012_auto_20211217_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleItemEmployee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField()),
                ('date_end', models.DateField(default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to=settings.AUTH_USER_MODEL)),
                ('account_2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees_2', to=settings.AUTH_USER_MODEL)),
                ('schedule_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='costasiella.scheduleitem')),
            ],
        ),
    ]
