# Generated by Django 3.1.5 on 2021-03-22 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0029_metastatic'),
    ]

    operations = [
        migrations.AddField(
            model_name='worktop_category',
            name='slug',
            field=models.SlugField(blank=True, default='slug', null=True),
        ),
    ]
