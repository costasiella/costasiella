# Generated by Django 3.1.9 on 2021-06-14 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0002_auto_20210614_0857'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organizationsubscriptiongroup',
            name='archived',
        ),
        migrations.AddField(
            model_name='organizationsubscriptiongroup',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
