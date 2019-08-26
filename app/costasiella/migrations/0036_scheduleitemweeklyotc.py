# Generated by Django 2.2.4 on 2019-08-26 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costasiella', '0035_auto_20190825_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleItemWeeklyOTC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time_start', models.TimeField()),
                ('time_end', models.TimeField()),
                ('display_public', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization_classtype', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='costasiella.OrganizationClasstype')),
                ('organization_level', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='costasiella.OrganizationLevel')),
                ('organization_location_room', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='costasiella.OrganizationLocationRoom')),
                ('schedule_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='costasiella.ScheduleItem')),
            ],
            options={
                'permissions': [('view_scheduleclassweeklyotc', 'Can view schedule class weekly one time change'), ('add_scheduleclassweeklyotc', 'Can add schedule class weekly one time change'), ('change_scheduleclassweeklyotc', 'Can change schedule class weekly one time change'), ('delete_scheduleclassweeklyotc', 'Can delete schedule class weekly one time change')],
            },
        ),
    ]
