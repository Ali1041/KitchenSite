import django_filters
from .models import *

class WorktopFilters(django_filters.FilterSet):
    class Meta:
        model = WorkTop
        fields = {
            # 'category':['exact'],
            'name':['icontains'],
            'price':['gte','lte']
        }


class AppliancesFilters(django_filters.FilterSet):
    class Meta:
        model = Appliances
        fields={
            'name':['icontains'],
            'appliances_type':['iexact'],
            'price':['gte','lte']
        }