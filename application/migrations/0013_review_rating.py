# Generated by Django 3.1.5 on 2021-01-12 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0012_cart_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='rating',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
