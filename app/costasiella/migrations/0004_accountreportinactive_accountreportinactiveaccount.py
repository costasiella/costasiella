# Generated by Django 3.2.13 on 2022-04-23 17:07

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0003_alter_scheduleitem_frequency_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountReportInactive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_activity_after_date', models.DateField(default=datetime.date(2021, 4, 23))),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AccountReportInactiveAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inactive_reports', to=settings.AUTH_USER_MODEL)),
                ('account_report_inactive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='costasiella.accountreportinactive')),
            ],
        ),
    ]
