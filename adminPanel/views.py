from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from application.models import *
from .forms import *
from django.conf import settings
from .models import *
import openpyxl
from openpyxl_image_loader import SheetImageLoader
from io import BytesIO
from django.core.files import File
from django.core.files.storage import default_storage
import os
# Create your views here.

def index(request):
    return render(request, 'adminPanel/admin_home.html')


# kitchen list admin
class ListKitchenView(generic.ListView):
    model = KitchenCategory
    template_name = 'adminPanel/admin_kitchen.html'
    context_object_name = 'kitchen_list'

    def get_context_data(self, *args, **kwargs):
        ctx = super(ListKitchenView, self).get_context_data(*args, **kwargs)
        ctx['product'] = 'Kitchen'
        return ctx


# kitchen detail

class KitchenDetailview(generic.ListView):
    model = Kitchen
    template_name = 'adminPanel/admin_kitchen_list_detail.html'
    context_object_name = 'kitchen_detail'

    def get_queryset(self):
        kitchen_category = KitchenCategory.objects.filter(pk=self.kwargs['pk'])
        return Kitchen.objects.select_related('kitchen_type').filter(kitchen_type=kitchen_category[0])


# kitchen add
def kitchenadd(request):
    ctx = {'form': KitchenForm}
    if request.method == 'POST':
        files = request.FILES.get('img')
        form = KitchenForm(request.POST or None, request.FILES or None)

        if form.is_valid():
            x = form.cleaned_data

            form.save(commit=True)
            # kitchen = Kitchen.objects.select_related('kitchen_type').get(kitchen_type=x['kitchen_type'],
            #                                                              color=x['color'], description=x['description'])
            #
            # # doors
            # door = Doors.objects.create(kitchen=kitchen, door_color=request.POST['door_color'])
            # door.door_img = request.FILES.get('door_img')
            # door.save()
            #
            # # cabnets
            # cabnets = Cabnets.objects.create(kitchen=kitchen, cabnet_color=request.POST['cabnet_color'])
            # cabnets.cabnet_img = request.FILES.get('cabnet_img')
            # cabnets.save()
            # img = Images.objects.create(kitchen=KitchenCategory.objects.get(name=x['kitchen_type']))
            # img.img = files
            # img.save()
            return redirect('adminPanel:admin-kitchen')

    return render(request, 'adminPanel/admin_add_kitchen.html', ctx)


# complete kitchen detail
class CompleteKitchenDetail(generic.DetailView):
    model = Kitchen
    template_name = 'adminPanel/admin_kitchen_detail.html'
    context_object_name = 'kitchen_detail'

    def get_context_data(self, **kwargs):
        ctx = super(CompleteKitchenDetail, self).get_context_data(**kwargs)
        kitchen = Kitchen.objects.select_related('kitchen_type').get(pk=self.kwargs['pk'])
        # doors = Doors.objects.select_related('kitchen').get(kitchen=kitchen)
        # cabnets = Cabnets.objects.select_related('kitchen').get(kitchen=kitchen)
        # ctx['doors'] = doors
        # ctx['cabnets'] = cabnets
        # ctx['imgs'] = Images.objects.select_related('kitchen').filter(kitchen=kitchen.kitchen_type)
        # print(ctx['imgs'].img)
        return ctx


# units for kitchen
class UnitsList(generic.ListView):
    model = Units
    paginate_by = 10
    template_name = 'adminPanel/units.html'
    context_object_name = 'units'

    def get_context_data(self, *args, **kwargs):
        kitchen = Kitchen.objects.select_related('kitchen_type').get(pk=self.kwargs['pk'])
        ctx = super(UnitsList, self).get_context_data(*args, **kwargs)
        ctx['kitchen'] = kitchen
        return ctx

    def get_queryset(self):
        kitchen = Kitchen.objects.select_related('kitchen_type').get(pk=self.kwargs['pk'])
        return Units.objects.select_related('kitchen').filter(kitchen=kitchen.kitchen_type)


def addunitcategory(request):
    if request.method == 'POST':
        x = UnitType.objects.create(name=request.POST['category'])
        x.save()
        return redirect('adminPanel:admin-add-units')


def addUnits(request, **kwargs):
    ctx = {'form': AddUnitsForm}
    if request.method == 'POST':
        if not kwargs:
            form = AddUnitsForm(request.POST or None, request.FILES or None)
            if form.is_valid():

                x = form.cleaned_data

                form.save(commit=True)
                return redirect(reverse_lazy('adminPanel:units',kwargs={'pk':KitchenCategory.objects.get(name=x['kitchen']).pk}))
        else:
            unit = Units.objects.get(pk=kwargs['pk'])
            img = unit.img
            unit.name = request.POST['name']
            unit.description = request.POST['description']
            unit.price = request.POST['price']
            unit.kitchen = KitchenCategory.objects.get(pk=request.POST['kitchen'])
            unit.unit_type = UnitType.objects.get(pk=request.POST['type'])
            if request.FILES.get('img') is not None:
                unit.img = request.FILES.get('img')
                unit.save()
            else:
                unit.img = img
                unit.save()

    if kwargs:
        ctx['item'] = Units.objects.select_related('unit_type').get(pk=kwargs['pk'])
        ctx['type'] = UnitType.objects.all()
        ctx['s_type'] = ctx['item'].unit_type
        ctx['kitchen'] = Kitchen.objects.select_related('kitchen_type').all()
        ctx['s_kitchen'] = ctx['item'].kitchen
        ctx['name'] = 'name'

    return render(request, 'adminPanel/add_units.html', ctx)


# worktop category
class WorkTypeCategory(generic.ListView):
    model = Worktop_category
    template_name = 'adminPanel/admin_worktops.html'
    context_object_name = 'category'

    def get_context_data(self, *args, **kwargs):
        ctx = super(WorkTypeCategory, self).get_context_data(*args, **kwargs)
        ctx['product'] = 'Worktop'
        return ctx


# add worktop category
def add_worktop_category(request, **kwargs):
    if request.method == 'POST':
        if kwargs['name'] == 'Worktop':
            Worktop_category.objects.create(worktop_type=request.POST['Worktop'])
            return redirect('adminPanel:admin-worktop')
        elif kwargs['name'] == 'Appliances':
            Category_Applianes.objects.create(name=request.POST['Appliances'])
            return redirect('adminPanel:admin-appliances')

        elif kwargs['name'] == 'Kitchen':
            KitchenCategory.objects.create(name=request.POST['Kitchen'])
            return redirect('adminPanel:admin-kitchen')


# worktop list on category basis
class WorktopList(generic.ListView):
    model = WorkTop
    paginate_by = 10
    template_name = 'adminPanel/admin_worktop_list.html'
    context_object_name = 'list'

    def get_context_data(self, *args, **kwargs):
        ctx = super(WorktopList, self).get_context_data(*args, **kwargs)
        ctx['product'] = 'Worktop'
        return ctx

    def get_queryset(self):
        worktop_category = Worktop_category.objects.get(pk=self.kwargs['pk'])
        worktop = WorkTop.objects.select_related('category').filter(category=worktop_category)
        return worktop


# worktop detail
class WorktopDetail(generic.DetailView):
    model = WorkTop
    template_name = 'adminPanel/admin_worktops_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(WorktopDetail, self).get_context_data(**kwargs)
        ctx['product'] = 'Worktop'
        return ctx

    def get_queryset(self):
        return WorkTop.objects.filter(pk=self.kwargs['pk'])


# adding/editing worktop
def add_worktop(request, **kwargs):
    # get request to display form
    if kwargs['name'] == 'Worktop':
        ctx = {'form': WorktopForm, 'product': 'Worktop'}
    else:
        ctx = {'form': AppliancesForm, 'product': 'Appliances'}

    if request.method == 'POST':

        # worktop
        if kwargs['name'] == 'Worktop':
            if len(kwargs) == 1:
                category = Worktop_category.objects.get(pk=request.POST['category'])
                form = WorktopForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save(commit=True)
                    return redirect(reverse_lazy('adminPanel:admin-worktop-list', kwargs={'pk': category.pk}))

            else:
                category = Worktop_category.objects.get(pk=request.POST['category'])

                x = WorkTop.objects.get(pk=kwargs['pk'])
                img = x.worktop_img
                x.category = category
                x.name = request.POST['name']
                x.color = request.POST['name']
                x.description = request.POST['description']
                x.price = request.POST['price']
                x.size = request.POST['size']
                if request.FILES.get('img') is None:
                    x.worktop_img = img
                else:
                    x.worktop_img = request.FILES.get('img')
                x.save()

                return redirect(reverse_lazy('adminPanel:admin-worktop-list', kwargs={'pk': category.pk}))


        # appliances
        else:

            if len(kwargs) == 1:
                form = AppliancesForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save(commit=True)
                    category = Category_Applianes.objects.get(pk=request.POST['category'])
                    return redirect(reverse_lazy('adminPanel:admin-appliances-list', kwargs={'pk': category.pk}))

            else:
                category = Category_Applianes.objects.filter(pk=request.POST['category'])
                price = float(request.POST['price'])
                a = Appliances.objects.get(pk=kwargs['pk'])
                img = a.img
                a.category.pk = category[0].pk
                a.name = request.POST['name']
                a.appliances_type = request.POST['type']
                a.description = request.POST['description']
                a.price = price
                a.brand_name = request.POST['brand']
                if request.FILES.get('img') is None:
                    a.img = img
                else:
                    a.img = request.FILES.get('img')
                a.save()
                return redirect(reverse_lazy('adminPanel:admin-appliances-list', kwargs={'pk': category[0].pk}))

    # get request with kwargs for or if editing a existing value
    if kwargs and len(kwargs) != 1:
        if kwargs['name'] == 'Appliances':
            ctx['add'] = 'add'
            ctx['item2'] = Appliances.objects.get(pk=kwargs['pk'])
            return render(request, 'adminPanel/admin_work_add.html', ctx)
        else:
            ctx['add2'] = 'add2'
            ctx['item'] = WorkTop.objects.get(pk=kwargs['pk'])
    return render(request, 'adminPanel/admin_work_add.html', ctx)


# appliances

# appliances category
class AppliancesCategory(generic.ListView):
    model = Category_Applianes
    template_name = 'adminPanel/admin_worktops.html'
    context_object_name = 'category'

    def get_context_data(self, *args, **kwargs):
        ctx = super(AppliancesCategory, self).get_context_data(*args, **kwargs)
        ctx['product'] = 'Appliances'
        return ctx


# appliances list based on category
class AppliancesList(generic.ListView):
    model = Appliances
    template_name = 'adminPanel/admin_worktop_list.html'
    context_object_name = 'list'

    def get_context_data(self, *args, **kwargs):
        ctx = super(AppliancesList, self).get_context_data(*args, **kwargs)
        ctx['product'] = 'Appliances'
        return ctx

    def get_queryset(self):
        category = Category_Applianes.objects.get(pk=self.kwargs['pk'])
        return Appliances.objects.filter(category=category)


# appliances detail
class AppliancesDetail(generic.DetailView):
    model = Appliances
    template_name = 'adminPanel/admin_worktops_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(AppliancesDetail, self).get_context_data(**kwargs)
        ctx['product'] = 'Appliances'
        return ctx


# Carts

# All orders
class Orders(generic.ListView):
    model = CompleteOrder
    template_name = 'adminPanel/admin_complete_orders.html'
    context_object_name = 'list'

    def get_queryset(self):
        x = CompleteOrder.objects.select_related('user').prefetch_related('order')
        return x


# detail order view
class DetailOrder(generic.DetailView):
    model = CompleteOrder
    template_name = 'adminPanel/admin_order_detail.html'
    context_object_name = 'detail'


# all users
def users(request):
    pass


class BlogsList(generic.ListView):
    model = Blogs
    template_name = 'adminPanel/admin_blogs.html'
    context_object_name = 'list'


def create_blog(request, **kwargs):
    form = BlogForm
    ctx = {'form': BlogForm}
    if len(kwargs) != 1:
        blog = get_object_or_404(Blogs, id=kwargs['pk'])
        form = BlogForm(request.POST or None, request.FILES or None, instance=blog)
        ctx['form'] = form
        ctx['blog'] = blog
    if request.method == 'POST':
        if kwargs['to'] == 'add':
            form = BlogForm(request.POST, request.FILES)
            if form.is_valid():
                form.save(commit=True)
                return redirect('adminPanel:admin-blog')

        else:
            blog = get_object_or_404(Blogs, id=kwargs['pk'])
            form = BlogForm(request.POST or None, request.FILES or None, instance=blog)
            if form.is_valid():
                if request.FILES:
                    form.save(commit=True)
                else:
                    form.title_img = blog.title_img
                    form.save(commit=True)
                return redirect('adminPanel:admin-blog')

    return render(request, 'adminPanel/blog_add.html', ctx)


class DetailBlog(generic.DetailView):
    model = Blogs
    template_name = 'adminPanel/blog-detail.html'
    context_object_name = 'detail'


def bulk_add(request):
    form = FileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse_lazy('adminPanel:reading',
                                         kwargs={'name': request.POST['name'], 'category': request.POST['category']}))

    return render(request, 'adminPanel/testupload.html', {'form': form})


def file_reading(request, **kwargs):
    file = UploadFile.objects.first()
    x = openpyxl.load_workbook(default_storage.open(file.file.name))
    if kwargs['name'] == 'appliance':
        worksheet = x[kwargs['category']]
        cat = Category_Applianes.objects.get(name=kwargs['category'])

        for i in range(1, worksheet.max_row + 1):
            if i == 1:
                pass
            else:
                img_loader = SheetImageLoader(worksheet)
                img = img_loader.get(f'G{i}')
                img_io = BytesIO()
                new_img = File(img_io, name=f'hobs_{i}')
                if img.mode in 'RGBA':
                    img = img.convert('RGB')
                img.save(img_io, 'JPEG', optimize=True)
                app = Appliances.objects.create(
                    name=worksheet.cell(row=i, column=3).value,
                    appliance_category=worksheet.cell(row=i, column=5).value,
                    category=cat,
                    brand_name=worksheet.cell(row=i, column=4).value,
                    description=worksheet.cell(row=i, column=6).value,
                    img=new_img,
                    appliances_type=worksheet.cell(row=i, column=8).value,
                    price=worksheet.cell(row=i, column=9).value
                )
                app.save()
        file.delete()
        return redirect('adminPanel:index')

    elif kwargs['name'] == 'worktop':
        y = x.sheetnames
        worksheet = x[y[0]]
        cat = Worktop_category.objects.get(worktop_type__iexact=kwargs['category'])
        for i in range(1, worksheet.max_row + 1):
            if i == 1:
                pass
            else:
                img_loader = SheetImageLoader(worksheet)
                img = img_loader.get(f'I{i}')
                img_io = BytesIO()
                new_img = File(img_io, name=f'worktop_{i}')
                if img.mode in 'RGBA':
                    img = img.convert('RGB')
                img.save(img_io, 'JPEG', optimize=True)
                app = WorkTop.objects.create(
                    name=worksheet.cell(row=i, column=4).value,
                    category=cat,
                    color=worksheet.cell(row=i, column=5).value,
                    size=worksheet.cell(row=i, column=6).value,
                    description=worksheet.cell(row=i, column=7).value,
                    worktop_img=new_img,
                    price=worksheet.cell(row=i, column=8).value
                )
                app.save()
        file.delete()
        return redirect('adminPanel:index')

    elif kwargs['name'] == 'kitchen':
        y = x.sheetnames
        worksheet = x[y[0]]
        cat = KitchenCategory.objects.get(name__iexact=kwargs['category'])
        for i in range(7, worksheet.max_row + 1):
            unit_cat = UnitType.objects.get_or_create(name=worksheet.cell(row=i, column=4).value)
            img_loader = SheetImageLoader(worksheet)
            img = img_loader.get(f'G{i}')
            img_io = BytesIO()
            if img.mode in 'P':
                img = img.convert('RGBA')
            img.save(img_io, 'PNG', optimize=True)
            new_img = File(img_io, name=f'kitchen_{i}')
            app = Units.objects.create(
                name=worksheet.cell(row=i, column=5).value,
                unit_type=unit_cat[0],
                kitchen=cat,
                description=worksheet.cell(row=i, column=6).value,
                price=worksheet.cell(row=i, column=8).value,
                sku=worksheet.cell(row=i, column=9).value,
                img=new_img

            )
            app.save()
        file.delete()
        return redirect('adminPanel:index')
    return render(request, 'adminPanel/file.html')


def approve(request):
    ctx={'comments':Review.objects.select_related('appliances','worktop').filter(approval = 'Pending')}
    return render(request,'adminPanel/comments.html',ctx)

def approving_admin(request,**kwargs):
    if kwargs['name'] == 'worktop':
        review = Review.objects.select_related('worktop','appliances').get(pk=kwargs['pk'])
        review.approval = 'Approved'
        review.save()
    else:
        review = Review.objects.select_related('worktop', 'appliances').get(pk=kwargs['pk'])
        review.approval = 'Approved'
        review.save()
    return redirect('adminPanel:approve')