# Generated by Django 3.1.5 on 2021-05-15 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0012_auto_20210515_0915'),
    ]

    operations = [
        migrations.AddField(
            model_name='financepaymentbatch',
            name='name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]