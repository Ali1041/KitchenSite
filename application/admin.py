from django.contrib import admin
from .models import *


# Register your models here.

class AdminKitchen(admin.ModelAdmin):
    list_display = ('kitchen_type',)
    list_filter = ('kitchen_type', 'color')
    search_fields = ('kitchen_type', 'color')


class AdminWorktop(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('category', 'name')
    search_fields = ('category', 'name')


class AdminUnits(admin.ModelAdmin):
    list_display = ('unit_type',)
    list_filter = ('unit_type', 'name', 'kitchen')
    search_fields = ('unit_type', 'name', 'kitchen')


admin.site.register(Kitchen, AdminKitchen)
admin.site.register(WorkTop, AdminWorktop)
admin.site.register(Units, AdminUnits)
admin.site.register(Appliances, AdminWorktop)
admin.site.register(Cart)
admin.site.register(Combining)
admin.site.register(CompleteOrder)
admin.site.register(Blogs)
admin.site.register(Color)
admin.site.register(Category_Applianes)
admin.site.register(Worktop_category)
admin.site.register(UserInfo)
admin.site.register(KitchenCategory)
admin.site.register(UnitType)
admin.site.register(Services)
admin.site.register(Units_intermediate)
admin.site.register(Newsletter)
admin.site.register(ContactUs)
admin.site.register(ContactActual)
admin.site.register(MetaStatic)
admin.site.register(AccessoriesType)
admin.site.register(Accessories)
admin.site.register(DemoChat)
admin.site.register(Review)