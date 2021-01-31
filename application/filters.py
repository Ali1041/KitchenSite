import django_filters
from .models import *
from django.db.models import Count
class WorktopFilters(django_filters.FilterSet):
    # name = django_filters.ModelChoiceFilter(
    #     queryset=WorkTop.objects.select_related('category').values('name').annotate(name__count=Count('name')))
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
        fields = ['unit_type']
