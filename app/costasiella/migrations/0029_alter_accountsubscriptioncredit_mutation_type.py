# Generated by Django 4.1.4 on 2022-12-24 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0028_accountsubscriptioncredit_reconciled_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountsubscriptioncredit',
            name='mutation_type',
            field=models.CharField(choices=[('SINGLE', 'Single'), ('ADD', 'Add'), ('SUB', 'Subtract')], default='SINGLE', max_length=255),
        ),
    ]
