# Generated by Django 4.2.5 on 2023-09-30 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0011_remove_timeslot_canceled_timeslot_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='is_new',
            field=models.BooleanField(default=True),
        ),
    ]
