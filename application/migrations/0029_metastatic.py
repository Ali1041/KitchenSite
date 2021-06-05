# Generated by Django 3.1.5 on 2021-03-15 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0028_auto_20210314_2353'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaStatic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home_title', models.CharField(max_length=255)),
                ('home_name', models.CharField(max_length=255)),
                ('home_description', models.TextField()),
                ('kitchen_title', models.CharField(max_length=255)),
                ('kitchen_name', models.CharField(max_length=255)),
                ('kitchen_description', models.TextField()),
                ('design_title', models.CharField(max_length=255)),
                ('design_name', models.CharField(max_length=255)),
                ('design_description', models.TextField()),
                ('install_title', models.CharField(max_length=255)),
                ('install_name', models.CharField(max_length=255)),
                ('install_description', models.TextField()),
                ('contact_title', models.CharField(max_length=255)),
                ('contact_name', models.CharField(max_length=255)),
                ('contact_description', models.TextField()),
                ('blog_title', models.CharField(max_length=255)),
                ('blog_name', models.CharField(max_length=255)),
                ('blog_description', models.TextField()),
                ('cancellation_title', models.CharField(max_length=255)),
                ('cancellation_name', models.CharField(max_length=255)),
                ('cancellation_description', models.TextField()),
                ('cookies_title', models.CharField(max_length=255)),
                ('cookies_name', models.CharField(max_length=255)),
                ('cookies_description', models.TextField()),
                ('disclaimer_title', models.CharField(max_length=255)),
                ('disclaimer_name', models.CharField(max_length=255)),
                ('disclaimer_description', models.TextField()),
                ('faq_title', models.CharField(max_length=255)),
                ('faq_name', models.CharField(max_length=255)),
                ('faq_description', models.TextField()),
                ('gdpr_title', models.CharField(max_length=255)),
                ('gdpr_name', models.CharField(max_length=255)),
                ('gdpr_description', models.TextField()),
                ('ip_title', models.CharField(max_length=255)),
                ('ip_name', models.CharField(max_length=255)),
                ('ip_description', models.TextField()),
                ('return_title', models.CharField(max_length=255)),
                ('return_name', models.CharField(max_length=255)),
                ('return_description', models.TextField()),
                ('shipping_title', models.CharField(max_length=255)),
                ('shipping_name', models.CharField(max_length=255)),
                ('shipping_description', models.TextField()),
                ('terms_title', models.CharField(max_length=255)),
                ('terms_name', models.CharField(max_length=255)),
                ('terms_description', models.TextField()),
            ],
        ),
    ]
