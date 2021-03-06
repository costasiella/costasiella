# Generated by Django 3.1.9 on 2021-06-15 09:02

import costasiella.modules.encrypted_fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0003_auto_20210614_1752'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_public', models.BooleanField(default=False)),
                ('display_shop', models.BooleanField(default=False)),
                ('display_backend', models.BooleanField(default=False)),
                ('title', costasiella.modules.encrypted_fields.EncryptedTextField(default='')),
                ('content', costasiella.modules.encrypted_fields.EncryptedTextField(default='')),
                ('date_start', models.DateField()),
                ('date_end', models.DateField(default=None, null=True)),
                ('priority', models.IntegerField(default=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
