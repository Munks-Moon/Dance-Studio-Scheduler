# Generated by Django 4.2.5 on 2023-09-16 22:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_timeslot'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
