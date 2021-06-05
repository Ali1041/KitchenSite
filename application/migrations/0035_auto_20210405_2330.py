# Generated by Django 3.1.5 on 2021-04-05 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0034_auto_20210404_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='metastatic',
            name='search_description',
            field=models.TextField(default='description'),
        ),
        migrations.AddField(
            model_name='metastatic',
            name='search_name',
            field=models.CharField(default='description', max_length=255),
        ),
        migrations.AddField(
            model_name='metastatic',
            name='search_title',
            field=models.CharField(default='description', max_length=255),
        ),
    ]
