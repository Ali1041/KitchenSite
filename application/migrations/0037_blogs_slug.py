# Generated by Django 3.1.5 on 2021-04-06 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0036_auto_20210405_2340'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogs',
            name='slug',
            field=models.SlugField(blank=True, default='slug', null=True),
        ),
    ]