# Generated by Django 3.2.14 on 2022-07-10 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0003_alter_insightaccountinactive_count_inactive_accounts'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleEventSubscriptionGroupDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization_subscription_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='costasiella.organizationsubscriptiongroup')),
                ('schedule_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='costasiella.scheduleevent')),
            ],
        ),
        migrations.AddField(
            model_name='scheduleevent',
            name='organization_subscription_groups',
            field=models.ManyToManyField(related_name='schedule_event_discounts', through='costasiella.ScheduleEventSubscriptionGroupDiscount', to='costasiella.OrganizationSubscriptionGroup'),
        ),
    ]
