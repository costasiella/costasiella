# Generated by Django 4.0.7 on 2022-10-31 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0018_organization_branding_color_accent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountfinancepaymentbatchcategoryitem',
            name='finance_payment_batch_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='costasiella.financepaymentbatchcategory'),
        ),
    ]