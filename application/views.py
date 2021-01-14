from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.core.serializers import serialize
from .filters import *
from django.views import generic
from django.core.paginator import Paginator
from django.urls import reverse_lazy
import json
from django.db.models import Q
from django.template.loader import render_to_string
from itertools import chain

# Create your views here.

User = get_user_model()


def signup(request):
    if request.method == 'POST':
        pas1 = request.POST['password']
        pas2 = request.POST['re_password']

        if pas1 != pas2:
            messages.warning(request, 'Password do not match')
            return redirect('application:signup')
        user = User.objects.create(username=request.POST['username'], email=request.POST['email'])
        user.set_password(pas1)
        user.save()
        return redirect('application:login')
    return render(request, 'signup.html')


def index(request):
    kitchen_styles = KitchenCategory.objects.all()
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'blogs': Blogs.objects.all()[:3], 'kitchen': kitchen_styles, 'appliances': appliances, 'worktop': worktop}

    return render(request, 'base.html', ctx)


# Ajax request to get photos for main page carosel
def img_urls(request, **kwargs):
    kitchen_type = KitchenCategory.objects.get(name=kwargs['name'])
    imgs = Images.objects.select_related('kitchen').filter(kitchen=kitchen_type)
    serialize_imgs = serialize('json', imgs)
    return JsonResponse(serialize_imgs, safe=False)


# all kitchen
class AllKitchenView(generic.ListView):
    model = KitchenCategory
    template_name = 'all_kitchen.html'
    context_object_name = 'list'

    def get_context_data(self, *args, **kwargs):
        ctx = super(AllKitchenView, self).get_context_data(*args, **kwargs)
        ctx['kitchen'] = KitchenCategory.objects.all()
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        return ctx


# view for kitchen display
class KitchenView(generic.ListView):
    model = Units
    template_name = 'kitchen.html'
    context_object_name = 'units'

    def get_context_data(self, *args, **kwargs):
        ctx = super(KitchenView, self).get_context_data(*args, **kwargs)
        ctx['kitchen'] = KitchenCategory.objects.all()
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        ctx['kitchen_view'] = KitchenCategory.objects.get(pk=self.kwargs['pk'])
        ctx['kitchen_color'] = Kitchen.objects.select_related('kitchen_type').filter(kitchen_type=ctx['kitchen_view'])
        ctx['imgs'] = Images.objects.select_related('kitchen').filter(kitchen=ctx['kitchen_view'])
        return ctx

    def get_queryset(self):
        kitchen_view = KitchenCategory.objects.get(pk=self.kwargs['pk'])
        units = Units.objects.select_related('kitchen').filter(kitchen=kitchen_view)
        return units


# Worktop list
class WorktopListView(generic.ListView):
    model = WorkTop
    template_name = 'worktop.html'
    context_object_name = 'list'

    def get_context_data(self, *args, **kwargs):
        ctx = super(WorktopListView, self).get_context_data(*args, **kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        ctx['kitchen'] = KitchenCategory.objects.all()

        filters = WorktopFilters(self.request.GET, queryset=WorkTop.objects.select_related('category').all())
        ctx['search'] = filters
        ctx['product'] = 'worktop'
        return ctx

    def get_queryset(self):
        category = Worktop_category.objects.get(pk=self.kwargs['pk'])
        x = WorkTop.objects.select_related('category').filter(category=category)
        filters = WorktopFilters(self.request.GET, queryset=WorkTop.objects.select_related('category').all())
        if len(self.request.GET) != 0:
            x = filters.qs
        return x


# worktop detail
class WorktopDetailView(generic.DetailView):
    model = WorkTop
    template_name = 'worktop_app_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(WorktopDetailView, self).get_context_data(**kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        one = WorkTop.objects.first()
        two = WorkTop.objects.last()
        three = Appliances.objects.first()
        four = Appliances.objects.last()
        ctx['feature1'] = [one,two]
        ctx['feature2'] = [three,four]
        if self.kwargs['name'] == 'worktop':
            ctx['product'] = 'worktop'
            ctx['review'] = Review.objects.select_related('worktop').filter(worktop_id=self.kwargs['pk'])
        elif self.kwargs['name'] == 'appliance':
            ctx['product'] = 'appliance'
            ctx['review'] = Review.objects.select_related('appliances').filter(appliances_id=self.kwargs['pk'])
        return ctx

    def get_queryset(self):
        if self.kwargs['name'] == 'worktop':
            worktop = WorkTop.objects.select_related('category').filter(pk=self.kwargs['pk'])
            return worktop
        elif self.kwargs['name'] == 'appliance':
            appliance = Appliances.objects.select_related('category').filter(pk=self.kwargs['pk'])
            return appliance


class AppliancesListView(generic.ListView):
    model = Appliances
    template_name = 'worktop.html'
    context_object_name = 'list'

    def get_context_data(self, *args, **kwargs):
        ctx = super(AppliancesListView, self).get_context_data(*args, **kwargs)
        ctx['kitchen'] = KitchenCategory.objects.all()
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        filters = AppliancesFilters(self.request.GET, queryset=Appliances.objects.select_related('category').all())
        ctx['search'] = filters
        ctx['product'] = 'appliance'
        return ctx

    def get_queryset(self):
        category = Category_Applianes.objects.get(pk=self.kwargs['pk'])
        x = Appliances.objects.select_related('category').filter(category=category)
        filters = AppliancesFilters(self.request.GET, queryset=Appliances.objects.select_related('category').all())
        if len(self.request.GET) != 0:
            x = filters.qs
        return x


def addcart(request, **kwargs):
    if not request.user.is_authenticated:
        return redirect('application:login')
    if kwargs['process'] == 'create':
        if kwargs['product'] == 'worktop':

            # worktop cart
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            try:
                my_cart = Cart.objects.get(user=request.user, worktop=worktop)
                x = my_cart.qty
                my_cart.qty = x + kwargs['qty']
                my_cart.save()
            except:
                my_cart = Cart.objects.create(user=request.user, worktop=worktop, qty=kwargs['qty'])

            return JsonResponse({'add': 'added'})
            # return redirect(rev)

        elif kwargs['product'] == 'appliance':

            # appliance cart
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.create(user=request.user, appliances=appliance, qty=kwargs['qty'])
            return JsonResponse({'add': 'added'})

            # return redirect('application:worktop-detail-view', kwargs={'pk': appliance.pk})

        elif kwargs['product'] == 'service':
            service = Services.objects.first()
            my_cart = Cart.objects.create(user=request.user, service=service)
            return redirect('application:cart')
        elif kwargs['product'] == 'sample':
            kitchen_cat = KitchenCategory.objects.get(pk=kwargs['pk'])
            kitchen = Kitchen.objects.filter(kitchen_type=kitchen_cat)
            unit = Units.objects.select_related('unit_type').filter(kitchen=kitchen_cat)
            door = Doors.objects.filter(kitchen=kitchen[0])
            cabnet = Cabnets.objects.filter(kitchen=kitchen[0])
            combine = Combining.objects.create(kitchen=kitchen[0], door=door[0], cabnet=cabnet[0], user=request.user)
            # combine.units.add(unit[0])
            my_cart = Cart.objects.create(kitchen_order=combine, user=request.user)

            return redirect('application:cart')

        else:
            # kitchen cart
            color = kwargs['product']
            name = kwargs['name']
            kitchen = Kitchen.objects.select_related('kitchen_type').get(
                kitchen_type=KitchenCategory.objects.get(name=name), color=color)
            unit = Units.objects.select_related('kitchen').get(pk=kwargs['pk'])

            try:
                pre_order = Combining.objects.select_related('kitchen').get(user=request.user, kitchen=kitchen)
                pre_order = pre_order
                pre_order.units.add(unit)
                pre_order.save()
                return redirect('application:cart')
            except:
                pre_order = Combining.objects.create(kitchen=kitchen, user=request.user)
                pre_order.units.add(unit)
                pre_order.save()
            return redirect(reverse_lazy('application:choose', kwargs={'pk': pre_order.pk}))


    elif kwargs['process'] == 'update':
        if kwargs['product'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.select_related('user','appliances').get(user=request.user,appliances=appliance)
            my_cart.qty = kwargs['qty']
            my_cart.save()
            return JsonResponse({'update': 'update'})

        elif kwargs['product'] == 'worktop':
                worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
                my_cart = Cart.objects.select_related('worktop','user').get(user=request.user,worktop=worktop)
                my_cart.qty = kwargs['qty']
                my_cart.save()
                return JsonResponse({'update':'update'})

    elif kwargs['process'] == 'delete':
        if kwargs['product'] == 'worktop':
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.filter(worktop_id=worktop.pk)
            my_cart.delete()
            return JsonResponse({'removed': 'removed'})

        elif kwargs['product'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.filter(appliances_id=appliance.pk)
            my_cart.delete()
            return JsonResponse({'removed': 'removed'})

        elif kwargs['product'] == 'service':
            service = Services.objects.first()
            my_cart = Cart.objects.filter(user=request.user, service=service)
            my_cart.delete()
            return JsonResponse({'removed': 'removed'})

        else:
            intermediate_model = Combining.objects.get(pk=kwargs['pk'])
            intermediate_model.delete()
            return JsonResponse({'removed': 'removed'})


def cart(request):
    if not request.user.is_authenticated:
        return redirect('application:login')
    kitchen_styles = KitchenCategory.objects.all()
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    cart = Cart.objects.select_related('kitchen_order', 'appliances', 'worktop', 'user').filter(user=request.user)
    price = 0
    for item in cart:
        if item.worktop:
            price += item.worktop.price*item.qty
        if item.appliances:
            price += item.appliances.price*item.qty
        if item.kitchen_order:
            if item.kitchen_order.units.all():
                for i in item.kitchen_order.units.all():
                    price += i.price
            else:
                price += 4.99

    ctx = {'cart': cart, 'kitchen': kitchen_styles, 'appliances': appliances, 'worktop': worktop, 'total': price}

    return render(request, 'cart.html', ctx)


# contact form page
def contact(request):
    if request.method == 'POST':
        return redirect('application:index')
    return render(request, 'contact_us.html')


# installation page
def installation(request):
    kitchen_styles = KitchenCategory.objects.all()
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'kitchen': kitchen_styles, 'appliances': appliances, 'worktop': worktop}

    return render(request, 'inc/installation.html', ctx)


# design page
def design(request):
    kitchen_styles = KitchenCategory.objects.all()
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'kitchen': kitchen_styles, 'appliances': appliances, 'worktop': worktop}

    return render(request, 'inc/design.html', ctx)


# wishlist
def wishlist(request, **kwargs):
    if not request.user.is_authenticated:
        return redirect('application:login')
    kitchen_styles = KitchenCategory.objects.all()
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    if kwargs:
        if kwargs['product'] == 'worktop':
            # worktop wishlist
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            WishList.objects.create(user=request.user, worktop=worktop)
            return redirect('application:list_wishlist')

        elif kwargs['product'] == 'appliance':
            # appliance wishlist
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            WishList.objects.create(user=request.user, appliances=appliance)
            return redirect('application:list_wishlist')
        else:
            # kitchen cart
            pass
    else:
        my_wishlist = WishList.objects.select_related('worktop', 'kitchen', 'unit', 'appliances').filter(
            user=request.user)
        ctx = {'wishlist': my_wishlist, 'kitchen': kitchen_styles, 'appliances': appliances, 'worktop': worktop}

        return render(request, 'wishlist.html', ctx)


def add_review(request, **kwargs):
    if request.method == 'POST':

        # appliance review addition
        if request.POST['name'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            review = Review.objects.create(
                user=request.user, rating=request.POST['rating'], comment=request.POST['comment'], appliances=appliance)
            return redirect(reverse_lazy('application:appliances-detail-view', kwargs={'pk': kwargs['pk']}))

        # worktop review addition
        elif request.POST['name'] == 'worktop':
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            Review.objects.create(
                user=request.user, rating=request.POST['rating'], comment=request.POST['comment'], worktop=worktop
            )
            return redirect(reverse_lazy('application:worktop-detail-view', kwargs={'pk': kwargs['pk']}))


def search(request, **kwargs):
    kitchen_styles = KitchenCategory.objects.all()
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    if request.method == 'POST':
        data = request.POST['search']
        # data = json.loads(request.body)
        qs1 = WorkTop.objects.filter(Q(name__icontains=data) | Q(description__icontains=data))
        qs2 = Appliances.objects.filter(Q(name__icontains=data) | Q(description__icontains=data))
        ctx = {'qs1': qs1, 'qs2': qs2, 'kitchen': kitchen_styles, 'appliances': appliances, 'worktop': worktop}

        return render(request, 'search.html', ctx)


def choose(request, **kwargs):
    if request.method == 'POST':
        intermediate_model = Combining.objects.select_related('kitchen', 'door', 'cabnet').get(user=request.user,
                                                                                               pk=kwargs['pk'])
        doors = Doors.objects.get(kitchen=intermediate_model.kitchen, door_color=request.POST['door'])
        cabnet = Cabnets.objects.get(kitchen=intermediate_model.kitchen, cabnet_color=request.POST['cabnet'])

        intermediate_model.door = doors
        intermediate_model.cabnet = cabnet
        intermediate_model.save()
        Cart.objects.create(kitchen_order=intermediate_model, user=request.user)
        if request.POST['cart'] == 'cart':
            return redirect('application:cart')
        else:
            return redirect('application:index')

    if request.method == 'GET':
        kitchen_styles = KitchenCategory.objects.all()
        worktop = Worktop_category.objects.all()
        appliances = Category_Applianes.objects.all()
        intermediate_model = Combining.objects.select_related('kitchen', 'door', 'cabnet').get(user=request.user,
                                                                                               pk=kwargs['pk'])
        doors = Doors.objects.filter(kitchen=intermediate_model.kitchen)
        cabnet = Cabnets.objects.filter(kitchen=intermediate_model.kitchen)
        ctx = {'kitchen': kitchen_styles, 'appliances': appliances, 'worktop': worktop, 'door': doors,
               'cabnets': cabnet, 'intermediate_model': intermediate_model}


    return render(request, 'proceed.html', ctx)


class BlogList(generic.ListView):
    model = Blogs
    template_name = 'blog.html'
    context_object_name = 'list'

    def get_context_data(self, **kwargs):
        ctx = super(BlogList, self).get_context_data(**kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        return ctx


class BlogDetail(generic.DetailView):
    model = Blogs
    template_name = 'blog_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(BlogDetail, self).get_context_data(**kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        return ctx


def newsletter(request):
    if request.body:
        data = json.loads(request.body)

        Newsletter.objects.create(email=data['email'])
        return JsonResponse({'added': 'added'})


def terms(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    return render(request, 'TERMS OF SERVICE 5 (40).html',ctx)


def disclaimer(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    return render(request, 'Disclaimer1 (37).html',ctx)


def cancel(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    return render(request, 'CANCELLATION POLICY (16).html',ctx)


def intellectual(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    return render(request, 'Intellectual Property Notification (8).html',ctx)


def Gdp(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    return render(request, 'GDPR Privacy Policy2 (44).html',ctx)


def FAQ(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    return render(request, 'FAQ.html',ctx)


def Return(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    return render(request, 'Return and Refund Policy (2) (6).html',ctx)


def ship(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    return render(request, 'Shipping and Delivery Policy 1 (22).html',ctx)


def cook(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}

    return render(request, 'Cookies Policy3 (42).html',ctx)
