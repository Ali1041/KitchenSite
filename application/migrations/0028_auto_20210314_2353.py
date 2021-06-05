# Generated by Django 3.1.5 on 2021-03-14 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0027_auto_20210312_2142'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accessoriestype',
            options={'ordering': ['-pk']},
        ),
        migrations.AddField(
            model_name='accessories',
            name='meta_description',
            field=models.TextField(blank=True, default='Accessories', null=True),
        ),
        migrations.AddField(
            model_name='accessories',
            name='meta_name',
            field=models.CharField(blank=True, default='Accessories', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='accessories',
            name='meta_title',
            field=models.CharField(blank=True, default='Accessories', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='accessoriestype',
            name='meta_description',
            field=models.TextField(blank=True, default='Accessories', null=True),
        ),
        migrations.AddField(
            model_name='accessoriestype',
            name='meta_name',
            field=models.CharField(blank=True, default='Accessories', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='accessoriestype',
            name='meta_title',
            field=models.CharField(blank=True, default='Accessories', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='appliances',
            name='meta_description',
            field=models.TextField(blank=True, default='Appliances', null=True),
        ),
        migrations.AddField(
            model_name='appliances',
            name='meta_name',
            field=models.CharField(blank=True, default='Appliances', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='appliances',
            name='meta_title',
            field=models.CharField(blank=True, default='Appliances', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='blogs',
            name='meta_description',
            field=models.TextField(blank=True, default='Accessories', null=True),
        ),
        migrations.AddField(
            model_name='blogs',
            name='meta_name',
            field=models.CharField(blank=True, default='Accessories', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='blogs',
            name='meta_title',
            field=models.CharField(blank=True, default='Accessories', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category_applianes',
            name='meta_description',
            field=models.TextField(blank=True, default='Category_Applianes', null=True),
        ),
        migrations.AddField(
            model_name='category_applianes',
            name='meta_name',
            field=models.CharField(blank=True, default='Category_Applianes', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category_applianes',
            name='meta_title',
            field=models.CharField(blank=True, default='Category_Applianes', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='kitchencategory',
            name='meta_description',
            field=models.TextField(blank=True, default='KitchenCategory', null=True),
        ),
        migrations.AddField(
            model_name='kitchencategory',
            name='meta_name',
            field=models.CharField(blank=True, default='KitchenCategory', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='kitchencategory',
            name='meta_title',
            field=models.CharField(blank=True, default='KitchenCategory', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='worktop',
            name='meta_description',
            field=models.TextField(blank=True, default='WorkTop', null=True),
        ),
        migrations.AddField(
            model_name='worktop',
            name='meta_name',
            field=models.CharField(blank=True, default='WorkTop', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='worktop',
            name='meta_title',
            field=models.CharField(blank=True, default='WorkTop', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='worktop_category',
            name='meta_description',
            field=models.TextField(blank=True, default='Worktop_category', null=True),
        ),
        migrations.AddField(
            model_name='worktop_category',
            name='meta_name',
            field=models.CharField(blank=True, default='Worktop_category', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='worktop_category',
            name='meta_title',
            field=models.CharField(blank=True, default='Worktop_category', max_length=255, null=True),
        ),
    ]
