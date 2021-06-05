# Generated by Django 3.1.5 on 2021-04-05 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0035_auto_20210405_2330'),
    ]

    operations = [
        migrations.AddField(
            model_name='metastatic',
            name='wishlist_description',
            field=models.TextField(default='description'),
        ),
        migrations.AddField(
            model_name='metastatic',
            name='wishlist_name',
            field=models.CharField(default='description', max_length=255),
        ),
        migrations.AddField(
            model_name='metastatic',
            name='wishlist_title',
            field=models.CharField(default='description', max_length=255),
        ),
    ]
