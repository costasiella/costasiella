# Generated by Django 3.1.13 on 2021-11-09 13:35

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0003_auto_20211109_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationclasstype',
            name='image',
            field=sorl.thumbnail.fields.ImageField(default=None, upload_to='organization_classtype'),
        ),
    ]