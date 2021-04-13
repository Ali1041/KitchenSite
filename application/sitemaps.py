from django.contrib import sitemaps
from django.urls import reverse
from .models import *

class StaticMaps(sitemaps.Sitemap):

    def items(self):
        return [
            'application:index',
            'application:installation',
            'application:design',
            'application:contact',
            'application:list_wishlist',
            'application:search',
            'application:installation_contact',
            'application:checkout',
            'application:terms',
            'application:shippping',
            'application:FAQ',
            'application:return-policy',
            'application:canel',
            'application:GDPR',
            'application:cookies',
            'application:disclaimer',
            'application:intelectual',
            'application:all-kitchen',
        ]

    def location(self, item):
        return reverse(item)


class WorktopMap(sitemaps.Sitemap):

    def items(self):
        return Worktop_category.objects.all()

class AppliancesMap(sitemaps.Sitemap):

    def items(self):
        return Category_Applianes.objects.all()

class AccessoriesList(sitemaps.Sitemap):

    def items(self):
        return AccessoriesType.objects.all()


class KitchenMap(sitemaps.Sitemap):

    def items(self):
        return Kitchen.objects.select_related('kitchen_type').all()

class WorktopsDetailMap(sitemaps.Sitemap):

    def items(self):
        return WorkTop.objects.select_related('category').all()

class AppliancesDetailMap(sitemaps.Sitemap):

    def items(self):
        return Appliances.objects.select_related('category').all()

class AccessoriesDetail(sitemaps.Sitemap):

    def items(self):
        return Accessories.objects.select_related('accessories_type').all()

class BlogsMap(sitemaps.Sitemap):
    def items(self):
        return Blogs.objects.all()