from django.db import models
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse

# Create your models here.


User = get_user_model()


class Color(models.Model):
    color_name = models.CharField(max_length=100)

    def __str__(self):
        return self.color_name


class KitchenCategory(models.Model):
    KITCHEN_TYPES = [
        ['OXFORD', 'OXFORD'],
        ['CARTMEL', 'CARTMEL'],
        ['WINDSOR', 'WINDSOR'],
        ['CAMBRIDGE', 'CAMBRIDGE'],
        ['LUCENTE MATT', 'LUCENTE MATT'],
        ['LUCENTE GLOSS', 'LUCENTE GLOSS'],
        ['Vivo+GLOSS', 'Vivo+GLOSS'],
        ['Vivo+MATT', 'Vivo+MATT'],
        ['Vivo+gloss for vero', 'Vivo+gloss for vero'],
        ['Vivo+matt for vero', 'Vivo+matt for vero'],
    ]
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name



class Kitchen(models.Model):
    kitchen_type = models.ForeignKey(KitchenCategory, on_delete=models.CASCADE)
    description = models.TextField()
    color = models.CharField(max_length=50)
    doors_guide = models.URLField(blank=True, null=True)
    tall_unit_guide = models.URLField(blank=True, null=True)
    x_tall_unit_guide = models.URLField(blank=True, null=True)
    carcases_tech_guide = models.URLField(blank=True, null=True)
    door_color = models.CharField(max_length=128, blank=True, null=True)
    cabnet = models.CharField(max_length=128, blank=True, null=True)
    img = models.ImageField(upload_to='kitchen', null=True, blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.kitchen_type.name} {self.color}'

    def get_photo_url(self):
        if self.img and hasattr(self.img, 'url'):
            return self.img.url

    def get_absolute_url(self):
        return reverse('application:kitchen-view', kwargs={'name': self.kitchen_type.name,'color':self.color})

    class Meta:
        ordering = ['-pk']
# class Doors(models.Model):
#     kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name='kitchen_door')
#     door_img = models.ImageField(upload_to='doors')
#
#     def __str__(self):
#         return self.kitchen.kitchen_type.name + ' door'
#
#     def get_photo_url(self):
#         if self.door_img and hasattr(self.door_img, 'url'):
#             return self.door_img.url


# class Cabnets(models.Model):
#     kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name='kitchen_cabnets')
#     door_color = models.CharField(max_length=128)
#     cabnet_img = models.ImageField(upload_to='cabnets')
#
#     def __str__(self):
#         return self.kitchen.kitchen_type.name + ' cabnets'
#
#     def get_photo_url(self):
#         if self.cabnet_img and hasattr(self.cabnet_img, 'url'):
#             return self.cabnet_img.url


# class Images(models.Model):
#     kitchen = models.ForeignKey(KitchenCategory, on_delete=models.CASCADE, related_name='kitchen_image')
#
#     def __str__(self):
#         return self.kitchen.name + ' picture'
#


class UnitType(models.Model):
    UNIT_TYPES = [
        ['BASE UNIT', 'BASE UNIT'],
        ['DRAWER UNIT', 'DRAWER UNIT'],
        ['LARDER UNIT', 'LARDER UNIT'],
        ['WALL UNIT', 'WALL UNIT'],
        ['APPLIANCE UNIT', 'APPLIANCE UNIT'],
        ['WIREWORK', 'WIREWORK'],
        ['PANEL', 'PANEL'],
        ['EXTRA DOOR', 'EXTRA DOOR'],

    ]
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Units(models.Model):
    name = models.CharField(max_length=255)
    unit_type = models.ForeignKey(UnitType, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()
    kitchen = models.ForeignKey(KitchenCategory, on_delete=models.CASCADE, related_name='kitchen_units')
    img = models.ImageField(upload_to='base_units')
    sku = models.CharField(max_length=255, default='SKU')
    added = models.BooleanField(default=False)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_photo_url(self):
        if self.img and hasattr(self.img, 'url'):
            return self.img.url

    class Meta:
        ordering = ['-pk']


class Worktop_category(models.Model):
    WORKTOP = [
        ['Wood Worktops', 'Wood Worktops'],
        ['Laminate worktops', 'Laminate worktops'],
        ['Solid Laminate Worktops', 'Solid Laminate Worktops'],
        ['Solid Surface Worktops', 'Solid Surface Worktops'],
        ['Stone Worktops', 'Stone Worktops'],

    ]
    worktop_type = models.CharField(max_length=255)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.worktop_type

    def get_absolute_url(self):
        return reverse('application:worktop-view', kwargs={'pk': self.id})


class WorkTop(models.Model):
    category = models.ForeignKey(Worktop_category, on_delete=models.CASCADE, related_name='worktop_category')
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    size = models.CharField(max_length=255)
    worktop_img = models.ImageField(upload_to='worktops/')
    added = models.BooleanField(default=False)
    available = models.BooleanField(default=True)

    # for_sample = models.CharField(max_length=10,blank=True,null=True,default='Yes')
    # sample_price = models.FloatField(blank=True,null=True,default=5)

    def __str__(self):
        return f'{self.name}'

    def get_photo_url(self):
        if self.worktop_img and hasattr(self.worktop_img, 'url'):
            return self.worktop_img.url

    def get_absolute_url(self):
        return reverse('application:worktop-detail-view', kwargs={'name':self.category.worktop_type,'pk': self.pk})

    class Meta:
        ordering = ['-pk']


class Category_Applianes(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('application:appliances-list', kwargs={'pk': self.id})

    class Meta:
        verbose_name_plural = 'Category_Appliances'
        ordering = ['-pk']


class Appliances(models.Model):
    category = models.ForeignKey(Category_Applianes, on_delete=models.CASCADE, related_name='appliance_category')
    name = models.CharField(max_length=255)
    appliances_type = models.CharField(max_length=255, default='none')
    brand_name = models.CharField(max_length=255, default='none')
    description = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='Appliance', default='none')
    price = models.FloatField()
    appliance_category = models.CharField(max_length=255)
    added = models.BooleanField(default=False)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('application:appliances-detail-view', kwargs={'name':self.category.name,'pk': self.id})

    def get_photo_url(self):
        if self.img and hasattr(self.img, 'url'):
            return self.img.url

    class Meta:
        ordering = ['-pk']


class Combining(models.Model):
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name='complete_kitchen')
    units = models.ManyToManyField(Units, through='Units_intermediate')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # door = models.ForeignKey(Doors, on_delete=models.CASCADE, blank=True, null=True)
    # cabnet = models.ForeignKey(Cabnets, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.kitchen.kitchen_type.name + 'purchased'


class Units_intermediate(models.Model):
    unit = models.ForeignKey(Units, on_delete=models.CASCADE, related_name='units_qty')
    combine = models.ForeignKey(Combining, on_delete=models.CASCADE)
    qty = models.IntegerField()

    def __str__(self):
        return str(self.qty)


class Services(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Cart(models.Model):
    kitchen_order = models.ForeignKey(Combining, on_delete=models.CASCADE, blank=True, null=True)
    worktop = models.ForeignKey(WorkTop, on_delete=models.CASCADE, blank=True, null=True)
    appliances = models.ForeignKey(Appliances, on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey(Services, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qty = models.IntegerField(blank=True, null=True)
    sample_worktop = models.CharField(max_length=100, default='No', blank=True, null=True)
    checkedout = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.kitchen_order:
            return f'{self.kitchen_order.kitchen.kitchen_type.name}'
        elif self.worktop:
            return self.worktop.name
        elif self.appliances:
            return self.appliances.name
        else:
            return self.service.name


class CompleteOrder(models.Model):
    order = models.ManyToManyField(Cart)
    user = models.ForeignKey('UserInfo', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + 'order'


class UserInfo(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.EmailField()
    phone_number = models.CharField(max_length=255)
    door_number = models.CharField(max_length=255, blank=True, null=True, )
    street_name = models.CharField(max_length=255, blank=True, null=True, )
    street_address = models.TextField(blank=True, null=True, default='none')
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name


class WishList(models.Model):
    worktop = models.ForeignKey(WorkTop, on_delete=models.CASCADE, blank=True, null=True)
    appliances = models.ForeignKey(Appliances, on_delete=models.CASCADE, blank=True, null=True)
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, blank=True, null=True)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return f'{self.user.username} wishlist'


class Blogs(models.Model):
    title = models.CharField(max_length=255)
    text = RichTextUploadingField()
    title_img = models.ImageField(upload_to='blog_img', default='hello')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_photo_url(self):
        if self.title_img and hasattr(self.title_img, 'url'):
            return self.title_img.url

    class Meta:
        verbose_name_plural = 'Blogs'
        ordering = ['-timestamp']


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    worktop = models.ForeignKey(WorkTop, on_delete=models.CASCADE, blank=True, null=True)
    appliances = models.ForeignKey(Appliances, on_delete=models.CASCADE, blank=True, null=True)
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, blank=True, null=True)
    approval_choices = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    ]
    approval = models.CharField(max_length=15, choices=approval_choices, default='Pending')
    rating = models.FloatField()
    comment = models.TextField()

    def __str__(self):
        return f'{self.user.username} review'


class Newsletter(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    site_address = models.TextField()
    phone = models.BigIntegerField()
    room_ready = models.BooleanField(default=False)
    remove_old_kitchen = models.BooleanField(default=False)
    require_things = models.BooleanField(default=False)
    your_budgets = models.CharField(max_length=100)
    detail = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']


class ContactActual(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    detail = models.TextField()
    phone = models.BigIntegerField()
    order_number = models.CharField(max_length=255)
    reason = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class MetaInfo(models.Model):
    home_title = models.CharField(max_length=255)
    home_name = models.CharField(max_length=255)
    home_description = models.TextField()

    kitchen_title = models.CharField(max_length=255)
    kitchen_name = models.CharField(max_length=255)
    kitchen_description = models.TextField()

    worktop_title = models.CharField(max_length=255)
    worktop_name = models.CharField(max_length=255)
    worktop_description = models.TextField()

    appliance_title = models.CharField(max_length=255)
    appliance_name = models.CharField(max_length=255)
    appliance_description = models.TextField()

    design_title = models.CharField(max_length=255)
    design_name = models.CharField(max_length=255)
    design_description = models.TextField()

    install_title = models.CharField(max_length=255)
    install_name = models.CharField(max_length=255)
    install_description = models.TextField()

    contact_title = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    contact_description = models.TextField()
