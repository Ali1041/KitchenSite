import django_filters
from .models import *
from django.db.models import Count
class WorktopFilters(django_filters.FilterSet):
    class Meta:
        model = WorkTop
        fields = {
            # 'category':['exact'],
            'price':['gte','lte'],
            'name':['iexact']
        }


class AppliancesFilters(django_filters.FilterSet):
    class Meta:
        model = Appliances
        fields={
            'appliance_category':['iexact'],
            # 'appliances_type':['iexact'],
            'price':['gte','lte']
        }

class UnitFilter(django_filters.FilterSet):
    class Meta:
        model = Units
        fields = {
            'unit_type':['exact'],
            'name':['icontains'],
            'description':['icontains']

            }


class AccessoriesFilter(django_filters.FilterSet):
    class Meta:
        model = Accessories
        fields = {
            'price': ['gte', 'lte']

        }
