# Generated by Django 4.0.7 on 2022-10-06 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0013_financequote_financequotegroup_financequoteitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='financequote',
            name='finance_quote_group',
            field=models.ForeignKey(default=100, on_delete=django.db.models.deletion.CASCADE, to='costasiella.financequotegroup'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='financequotegroup',
            name='prefix',
            field=models.CharField(default='QUO', max_length=255),
        ),
    ]