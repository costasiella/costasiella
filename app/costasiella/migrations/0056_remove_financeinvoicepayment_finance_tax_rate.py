# Generated by Django 2.2.8 on 2019-12-30 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0055_financeinvoicepayment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financeinvoicepayment',
            name='finance_tax_rate',
        ),
    ]
