# Generated by Django 3.1.5 on 2021-02-04 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0011_auto_20210205_0300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='region',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
