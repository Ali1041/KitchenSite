# Generated by Django 3.1.5 on 2021-01-28 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_auto_20210127_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='email_address',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
