# Generated by Django 3.1.5 on 2021-03-10 17:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0025_wishlist_accessories'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='accessories',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='application.accessories'),
        ),
    ]