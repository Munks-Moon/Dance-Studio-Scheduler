# Generated by Django 4.2.5 on 2023-10-03 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0013_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='invoices/'),
        ),
    ]
