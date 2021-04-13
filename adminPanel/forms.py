from django import forms
from application.models import *
from .models import *


class WorktopForm(forms.ModelForm):
    class Meta:
        model = WorkTop
        fields = '__all__'


class AppliancesForm(forms.ModelForm):
    class Meta:
        model = Appliances
        fields = '__all__'


class KitchenForm(forms.ModelForm):
    class Meta:
        model = Kitchen
        fields = '__all__'


#
# class ImagesForm(forms.ModelForm):
#     class Meta:
#         model = Images
#         exclude = ['kitchen', ]
#
#
# class DoorsForm(forms.ModelForm):
#     class Meta:
#         model = Doors
#         exclude = ('kitchen',)
#
#     def save(self, commit=False):
#         return super(DoorsForm, self).save(commit)
#
#
# class CabnetsForm(forms.ModelForm):
#     class Meta:
#         model = Cabnets
#         exclude = ('kitchen',)
#
#     def save(self, commit=False):
#         return super(CabnetsForm, self).save(commit)


class AddUnitsForm(forms.ModelForm):
    class Meta:
        model = Units
        fields = '__all__'


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blogs
        exclude = ['timestamp', ]


class FileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = '__all__'


class AccessoriesForm(forms.ModelForm):
    class Meta:
        model = Accessories
        fields = '__all__'
