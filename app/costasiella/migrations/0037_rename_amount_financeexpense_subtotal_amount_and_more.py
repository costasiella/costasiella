# Generated by Django 4.1.7 on 2023-03-09 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0036_remove_financeexpense_subtotal_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='financeexpense',
            old_name='amount',
            new_name='subtotal_amount',
        ),
        migrations.RenameField(
            model_name='financeexpense',
            old_name='percentage_tax',
            new_name='subtotal_tax',
        ),
        migrations.RenameField(
            model_name='financeexpense',
            old_name='percentage_amount',
            new_name='total_amount',
        ),
        migrations.RemoveField(
            model_name='financeexpense',
            name='percentage_total',
        ),
        migrations.RemoveField(
            model_name='financeexpense',
            name='tax',
        ),
        migrations.AddField(
            model_name='financeexpense',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='financeexpense',
            name='total_tax',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
            preserve_default=False,
        ),
    ]