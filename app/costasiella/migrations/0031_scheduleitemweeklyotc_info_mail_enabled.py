# Generated by Django 4.1.4 on 2023-01-05 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0030_scheduleitem_info_mail_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduleitemweeklyotc',
            name='info_mail_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
