# Generated by Django 4.0.7 on 2022-10-16 17:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0015_rename_due_after_days_financequotegroup_expires_after_days'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=255)),
                ('system_mail_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='costasiella.systemmailtemplate')),
            ],
        ),
        migrations.CreateModel(
            name='SystemNotificationAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('system_notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='costasiella.systemnotification')),
            ],
        ),
    ]