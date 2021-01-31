from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib.auth import authenticate, login as log
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.core.serializers import serialize
from .filters import *
from django.views import generic
from django.urls import reverse_lazy
import json
from django.db.models import Q
from itertools import chain
from django.db.models import Count
import random
from .forms import *
import klarnacheckout
import requests
import base64
from django.core.mail import send_mail

# Create your views here.
User = get_user_model()


def signup(request):
    if request.method == 'POST':
        pas1 = request.POST['password']
        pas2 = request.POST['re_password']

        if pas1 != pas2:
            messages.warning(request, 'Password do not match')
            return redirect('application:signup')
        already_exist = User.objects.filter(email=request.POST['email'])
        if already_exist:
            messages.warning(request, 'This email is already registered. Try again with a different one.')
            return redirect('application:signup')
        try:
            user = User.objects.create(username=request.POST['username'], email=request.POST['email'])
        except:
            msg = messages.warning(request, 'This username is taken. Enter a different one,')
            return render(request, 'signup.html', {'messages': messages})
        user.set_password(pas1)
        user.save()
        send_mail(
            'Registered Successfully!!',
            'Congratulations, you have registered successfully. Login now to see exclusive deals.',
            None,
            [user.email],
            fail_silently=True
        )
        msg = messages.success(request, "You've registered successfully. Please Login to view prices & latest offers.")
        return redirect('application:login')
    return render(request, 'signup.html')


def login(request):
    redirect_to = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        # raise ValueError('sad')
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            log(request, user)
            if redirect_to and request.POST['url'] != 'http://127.0.0.1:8000/signup/' and request.POST[
                'url'] != 'http://127.0.0.1:8000/login/':
                return redirect(request.POST['url'])
            else:
                return redirect('application:index')
    return render(request, 'registration/login.html', {'url': redirect_to})


def cart_count(request):
    if request.user.is_authenticated:
        return Cart.objects.select_related('user').filter(user=request.user,checkedout=False)


def index(request):
    user_cart = cart_count(request)
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'blogs': Blogs.objects.all()[:3], 'cart_count': user_cart, 'appliances': appliances, 'worktop': worktop}

    return render(request, 'base.html', ctx)


# Ajax request to get photos for main page carousel
def img_urls(request, **kwargs):
    if kwargs['name'] == 'View all':
        kitchens = Kitchen.objects.select_related('kitchen_type').all()
        imgs = kitchens.annotate(count=Count('kitchen_type')).order_by()
    else:
        kitchen_type = KitchenCategory.objects.get(name=kwargs['name'])
        imgs = Kitchen.objects.select_related('kitchen_type').filter(kitchen_type=kitchen_type)
    serialize_imgs = serialize('json', imgs)
    return JsonResponse(serialize_imgs, safe=False)


# all kitchen
class AllKitchenView(generic.ListView):
    model = Kitchen
    template_name = 'all_kitchen.html'
    context_object_name = 'list'

    def get_context_data(self, *args, **kwargs):
        ctx = super(AllKitchenView, self).get_context_data(*args, **kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        ctx['cart_count'] = cart_count(self.request)

        return ctx

    def get_queryset(self):
        kitchens = KitchenCategory.objects.all()
        list_of_kitchen = []

        for item in kitchens:
            x = Kitchen.objects.select_related('kitchen_type').filter(kitchen_type=item)
            if x:
                list_of_kitchen.append(x)
        # remove_duplicate = list(set(list_of_kitchen))
        # print(remove_duplicate)
        return list_of_kitchen


# view for kitchen display
class KitchenView(generic.ListView):
    model = Units
    paginate_by = 10
    template_name = 'kitchen.html'
    context_object_name = 'units'

    def get_context_data(self, *args, **kwargs):
        ctx = super(KitchenView, self).get_context_data(*args, **kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        ctx['kitchen_view'] = KitchenCategory.objects.get(pk=self.kwargs['pk'])
        ctx['search'] = UnitType.objects.all()
        ctx['cart_count'] = cart_count(self.request)

        ctx['kitchen_color'] = Kitchen.objects.select_related('kitchen_type').filter(kitchen_type=ctx['kitchen_view'])
        # ctx['imgs'] = Images.objects.select_related('kitchen').filter(kitchen=ctx['kitchen_view'])
        return ctx

    def get_queryset(self):
        kitchen_view = KitchenCategory.objects.get(pk=self.kwargs['pk'])
        units = Units.objects.select_related('kitchen').filter(kitchen=kitchen_view)
        filters = UnitFilter(self.request.GET,
                             queryset=Units.objects.select_related('kitchen').filter(kitchen=kitchen_view))
        if len(self.request.GET) != 0:
            units = filters.qs
        return units


# Worktop list
class WorktopListView(generic.ListView):
    model = WorkTop
    template_name = 'worktop.html'
    context_object_name = 'list'
    paginate_by = 10

    # page_kwarg = 'pk'

    def get_queryset(self):
        category = Worktop_category.objects.get(pk=self.kwargs['pk'])
        qs = WorkTop.objects.select_related('category').filter(category=category)
        filters = WorktopFilters(self.request.GET, queryset=qs)
        if len(self.request.GET) != 0:
            qs = filters.qs
        if category.worktop_type == 'Stone Worktops':
            qs = ['stone', 'stone']
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super(WorktopListView, self).get_context_data(*args, **kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        ctx['cart_count'] = cart_count(self.request)

        try:
            category_based_worktop = WorkTop.objects.select_related('category').filter(
                category=self.get_queryset().first().category)
            number_of_worktop_in_category = category_based_worktop.values('name').annotate(
                count=Count('name')).order_by()
            select_list = []
            for item in number_of_worktop_in_category:
                select_list.append(item['name'])
            ctx['select'] = select_list
        except:
            if self.get_queryset():
                if self.get_queryset()[0] == 'stone':
                    ctx['stone'] = 'stone'

        # filters = WorktopFilters(self.request.GET, queryset=WorkTop.objects.select_related('category').all())
        # ctx['search'] = filters
        ctx['product'] = 'worktop'
        return ctx

# random queryset
def random_queryset():
    one = list(WorkTop.objects.all())
    random_sample = random.sample(one, 2)
    three = list(Appliances.objects.all())
    random_sample_2 = random.sample(three, 2)
    return random_sample,random_sample_2

# worktop detail
class WorktopDetailView(generic.DetailView):
    model = WorkTop
    template_name = 'worktop_app_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(WorktopDetailView, self).get_context_data(**kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        ctx['cart_count'] = cart_count(self.request)
        ctx['feature1'] = random_queryset()[0]
        ctx['feature2'] = random_queryset()[1]
        if self.kwargs['name'] == 'worktop':
            ctx['product'] = 'worktop'
            ctx['review'] = Review.objects.select_related('worktop').filter(worktop_id=self.kwargs['pk'],
                                                                            approval='Approved')
        elif self.kwargs['name'] == 'appliance':
            ctx['product'] = 'appliance'
            ctx['review'] = Review.objects.select_related('appliances').filter(appliances_id=self.kwargs['pk'],
                                                                               approval='Approved')
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
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        ctx = super(AppliancesListView, self).get_context_data(*args, **kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        ctx['cart_count'] = cart_count(self.request)

        try:
            category_based_appliances = Appliances.objects.select_related('category').filter(
                category=self.get_queryset().first().category)
            num_of_appliances_in_category = category_based_appliances.values('appliance_category').annotate(
                count=Count('appliance_category')).order_by()
            select_list = []
            for item in num_of_appliances_in_category:
                select_list.append(item['appliance_category'])
            ctx['select'] = select_list
        except:
            pass
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
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])

            if kwargs['name'] == 'sample':
                my_cart = Cart.objects.create(user=request.user, worktop=worktop, qty=1, sample_worktop='Yes')
                return JsonResponse({'added': 'added'})
            # worktop cart
            try:
                my_cart = Cart.objects.get(user=request.user, worktop=worktop,checkedout=False)
                x = my_cart.qty
                my_cart.qty = x + kwargs['qty']
                my_cart.save()
            except:
                my_cart = Cart.objects.create(user=request.user, worktop=worktop, qty=kwargs['qty'])

            return JsonResponse({'add': 'added'})
            # return redirect(rev)

        elif kwargs['product'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            try:
                my_cart = Cart.objects.get(user=request.user, appliances=appliance,checkedout=False)
                x = my_cart.qty
                my_cart.qty = x + kwargs['qty']
                my_cart.save()
            except:
                # appliance cart
                my_cart = Cart.objects.create(user=request.user, appliances=appliance, qty=kwargs['qty'])
            return JsonResponse({'add': 'added'})

            # return redirect('application:worktop-detail-view', kwargs={'pk': appliance.pk})

        elif kwargs['product'] == 'service':
            service = Services.objects.get_or_create(name='Service')
            my_cart = Cart.objects.create(user=request.user, service=service[0])
            return redirect('application:cart')

        elif kwargs['product'] == 'sample':
            kitchen_cat = KitchenCategory.objects.get(pk=kwargs['pk'])
            kitchen = Kitchen.objects.filter(kitchen_type=kitchen_cat)
            # unit = Units.objects.select_related('unit_type').filter(kitchen=kitchen_cat)
            combine = Combining.objects.create(kitchen=kitchen[0], user=request.user)
            # combine.units.add(unit[0])
            my_cart = Cart.objects.create(kitchen_order=combine, user=request.user)

            return redirect('application:cart')

        else:
            # kitchen cart
            color = kwargs['product']
            name = kwargs['name']
            qty = kwargs['qty']
            try:
                kitchen = Kitchen.objects.select_related('kitchen_type').get(
                    kitchen_type=KitchenCategory.objects.get(name=name), color=color)
            except:
                cat = KitchenCategory.objects.get(name__iexact=kwargs['name'])
                return redirect(reverse_lazy('application:kitchen-view', kwargs={'pk': cat.pk}))
            unit = Units.objects.select_related('kitchen').get(pk=kwargs['pk'])

            pre_order = Combining.objects.select_related('kitchen').filter(user=request.user, kitchen=kitchen)
            if pre_order:
                already_exist = Units_intermediate.objects.select_related('unit', 'combine').filter(unit_id=unit.pk)
                if already_exist:
                    already_exist[0].qty = qty + already_exist[0].qty
                    already_exist[0].save()
                else:
                    print('inside else')
                    unit_inter = Units_intermediate.objects.create(unit=unit, qty=qty, combine=pre_order[0])
                    pre_order[0].save()
                    unit_inter.save()
            else:
                pre_order = Combining.objects.create(kitchen=kitchen, user=request.user)
                unit_inter = Units_intermediate.objects.create(unit=unit, combine=pre_order, qty=qty)
                pre_order.save()
                unit_inter.save()
                Cart.objects.create(kitchen_order=pre_order, user=request.user)
            return JsonResponse({'added': 'added'})


    elif kwargs['process'] == 'update':
        if kwargs['product'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.select_related('user', 'appliances').get(user=request.user,checkedout=False, appliances=appliance)
            my_cart.qty = kwargs['qty']
            my_cart.save()
            return JsonResponse({'update': 'update'})

        elif kwargs['product'] == 'worktop':
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.select_related('worktop', 'user').get(user=request.user, worktop=worktop,checkedout=False)
            my_cart.qty = kwargs['qty']
            my_cart.save()
            return JsonResponse({'update': 'update'})

    elif kwargs['process'] == 'delete':
        if kwargs['product'] == 'worktop':
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.filter(worktop_id=worktop.pk,checkedout=False)
            my_cart.delete()
            return JsonResponse({'removed': 'removed'})

        elif kwargs['product'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.filter(appliances_id=appliance.pk,checkedout=False)
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
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    cart = Cart.objects.select_related('kitchen_order', 'appliances', 'worktop', 'user').filter(user=request.user,checkedout=False)
    price = 0
    worktop_cart = []
    appliances_cart = []
    for_check1 = True
    for_check2 = True
    sample_price = 0
    service = ''
    for item in cart:
        if item.worktop:

            if item.sample_worktop == 'Yes':
                for_check1 = False
                sample_price += 5
            else:
                price += item.worktop.price * item.qty
            worktop_cart.append(item)
        if item.appliances:
            price += item.appliances.price * item.qty
            appliances_cart.append(item)
        if item.kitchen_order:
            if item.kitchen_order.units_intermediate_set.all():
                for i in item.kitchen_order.units_intermediate_set.all():
                    price += i.unit.price * i.qty
            else:
                sample_price += 4.99
        if item.service:
            service = 'service'
            sample_price += 50
            for_check2 = False
    if price < 300 and price != 0:
        price += 30
    price = price + sample_price
    ctx = {'cart': cart, 'service': service, 'worktop_cart': worktop_cart, 'appliances_cart': appliances_cart,
           'appliances': appliances, 'worktop': worktop, 'total': price, 'feature1': random_queryset()[0],
           'feature2': random_queryset()[1], 'cart_count': cart_count(request)}

    return render(request, 'cart.html', ctx)


# contact form page
def contact(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    if request.method == 'POST':
        return redirect('application:index')
    ctx = {'appliances': appliances, 'worktop': worktop, 'cart_count': cart_count(request)}

    return render(request, 'contact_us.html',ctx)


# installation page
def installation(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'inc/installation.html', ctx)


# design page
def design(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'inc/design.html', ctx)


# wishlist
def wishlist(request, **kwargs):
    if not request.user.is_authenticated:
        return redirect('application:login')
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
        ctx = {'wishlist': my_wishlist, 'appliances': appliances, 'worktop': worktop}
        ctx['cart_count'] = cart_count(request)

        return render(request, 'wishlist.html', ctx)


def add_review(request, **kwargs):
    if request.method == 'POST':

        # appliance review addition
        if request.POST['name'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            review = Review.objects.create(
                user=request.user, rating=request.POST['rating'], comment=request.POST['comment'], appliances=appliance,
                approval='Pending')
            return redirect(
                reverse_lazy('application:appliances-detail-view', kwargs={'name': 'appliance', 'pk': appliance.pk}))

        # worktop review addition
        elif request.POST['name'] == 'worktop':
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            Review.objects.create(
                user=request.user, rating=request.POST['rating'], comment=request.POST['comment'], worktop=worktop,
                approval='Pending'
            )
            return redirect(
                reverse_lazy('application:worktop-detail-view', kwargs={'name': 'worktop', 'pk': kwargs['pk']}))


def search(request, **kwargs):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    if request.method == 'POST':
        data = request.POST['search']
        # data = json.loads(request.body)
        qs1 = WorkTop.objects.filter(Q(name__icontains=data) | Q(description__icontains=data))
        qs2 = Appliances.objects.filter(Q(name__icontains=data) | Q(description__icontains=data))
        ctx = {'qs1': qs1, 'qs2': qs2, 'appliances': appliances, 'worktop': worktop}
        ctx['cart_count'] = cart_count(request)

        return render(request, 'search.html', ctx)


class BlogList(generic.ListView):
    model = Blogs
    template_name = 'blog.html'
    context_object_name = 'list'

    def get_context_data(self, **kwargs):
        ctx = super(BlogList, self).get_context_data(**kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        ctx['cart_count'] = cart_count(self.request)

        return ctx


class BlogDetail(generic.DetailView):
    model = Blogs
    template_name = 'blog_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(BlogDetail, self).get_context_data(**kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        ctx['cart_count'] = cart_count(self.request)

        return ctx


def newsletter(request):
    if request.body:
        data = json.loads(request.body)
        already_exist = Newsletter.objects.filter(email=data['email'])
        if already_exist:
            return JsonResponse({'added': 'not added'})
        Newsletter.objects.create(email=data['email'])
        send_mail(
            'Subscribed Successfully!!',
            'Congratulations, you have subscribed to our newsletter.',
            None,
            [data['email']],
            fail_silently=True
        )
        return JsonResponse({'added': 'added'})


def terms(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'TERMS OF SERVICE 5 (40).html', ctx)


def disclaimer(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'Disclaimer1 (37).html', ctx)


def cancel(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'CANCELLATION POLICY (16).html', ctx)


def intellectual(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'Intellectual Property Notification (8).html', ctx)


def Gdp(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'GDPR Privacy Policy2 (44).html', ctx)


def FAQ(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'FAQ.html', ctx)


def Return(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'Return and Refund Policy (2) (6).html', ctx)


def ship(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'Shipping and Delivery Policy 1 (22).html', ctx)


def cook(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    ctx['cart_count'] = cart_count(request)

    return render(request, 'Cookies Policy3 (42).html', ctx)


def install_contact(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    if request.method == 'POST':
        ContactUs.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            site_address=request.POST['address'],
            detail=request.POST['detail'],
            room_ready=request.POST['measure'],
            remove_old_kitchen=request.POST['old'],
            require_things=request.POST['ee'],
            your_budgets=request.POST['price'],

        )
        return redirect('application:index')

    ctx = {'appliances': appliances, 'worktop': worktop, 'cart_count': cart_count(request)}

    return render(request, 'installation_contact.html', ctx)


def unit_change(request, **kwargs):
    if kwargs['name'] == 'change':
        unit_intermediate = Units_intermediate.objects.select_related('unit', 'combine').get(pk=kwargs['pk'])
        unit_intermediate.qty = kwargs['qty']
        unit_intermediate.save()
    elif kwargs['name'] == 'delete':
        unit_intermediate = Units_intermediate.objects.select_related('unit', 'combine').get(pk=kwargs['pk'])
        unit_intermediate.delete()

    return JsonResponse({'changed': 'changed'})


# checkout view
def checkout(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    form = UserInfoForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            info = UserInfo.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email_address=data['email_address'],
                phone_number=data['phone_number'],
                street_address=data['street_address'],
                city=data['city'],
                region=data['region'],
                postcode=data['postcode'],
                country=data['country'],
            )
            request.session['user_info_pk'] = info.pk
            return redirect('application:create-order')
    ctx = {'form': form,'appliances': appliances, 'worktop': worktop,'cart_count':cart_count(request)}
    return render(request, 'checkout.html', ctx)


def create_order_klarna(request, **kwargs):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    base_url = 'https://api.playground.klarna.com'
    url = base_url + '/checkout/v3/orders'

    my_items = Cart.objects.select_related('kitchen_order', 'worktop', 'appliances', 'user').filter(user=request.user)
    raw_data = {
        "purchase_country": "GB",
        "purchase_currency": "GBP",
        "locale": "en-GB",
        "order_amount": 0,
        "order_tax_amount": 0,
        "order_lines": [

        ],
        "merchant_urls": {
            "terms": "https://www.example.com/terms.html",
            "checkout": "https://www.example.com/checkout.html?order_id={checkout.order.id}",
            "confirmation": "http://127.0.0.1:8000/order-confirmed/",
            "push": "http://127.0.0.1:8000/push-email/",
        },
    }

    price = 0
    sample_price = 0
    cal_total_tax = 0
    for item in my_items:
        if item.worktop:
            if item.sample_worktop == 'Yes':
                sample_price += 5
                # total amount
                f_price = 5 * 100

                # total tax
                this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)

                # added tax to total tax
                cal_total_tax += this_item_tax
                item_dict = {
                    "type": "physical",
                    "reference": "19-402-USA",
                    "name": f'{item.worktop.name} Sample',
                    "quantity": item.qty,
                    "quantity_unit": "pcs",
                    "unit_price": f_price,
                    "tax_rate": 2000,
                    "total_amount": f_price,
                    "total_discount_amount": 0,
                    "total_tax_amount": this_item_tax
                }
                raw_data['order_lines'].append(item_dict)
            else:
                # total amount
                f_price = int(item.worktop.price * item.qty * 100)

                # total tax
                this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)

                # added tax to total tax
                cal_total_tax += this_item_tax
                price += item.worktop.price * item.qty
                item_dict = {
                    "type": "physical",
                    "reference": "19-402-USA",
                    "name": f'{item.worktop.name}',
                    "quantity": item.qty,
                    "quantity_unit": "pcs",
                    "unit_price": int(item.worktop.price * 100),
                    "tax_rate": 2000,
                    "total_amount": f_price,
                    "total_discount_amount": 0,
                    "total_tax_amount": this_item_tax
                }
                raw_data['order_lines'].append(item_dict)
        if item.appliances:
            price += item.appliances.price * item.qty

            # total amount
            f_price = int(item.appliances.price * item.qty * 100)

            # total tax
            this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)

            # added tax to total tax
            cal_total_tax += this_item_tax
            item_dict = {
                "type": "physical",
                "reference": "19-402-USA",
                "name": f'{item.appliances.name}',
                "quantity": item.qty,
                "quantity_unit": "pcs",
                "unit_price": int(item.appliances.price * 100),
                "tax_rate": 2000,
                "total_amount": f_price,
                "total_discount_amount": 0,
                "total_tax_amount": this_item_tax
            }
            raw_data['order_lines'].append(item_dict)
        if item.kitchen_order:
            if item.kitchen_order.units_intermediate_set.all():
                for i in item.kitchen_order.units_intermediate_set.all():
                    # total amount
                    f_price = int(int(i.unit.price + (i.unit.price * 20 / 100)) * i.qty * 100)
                    # separate_tax = f_price*20/100
                    # print(separate_tax)
                    #
                    # f_price = int(f_price+separate_tax)
                    # total tax
                    this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)

                    # tax cal
                    # f_price = f_price+this_item_tax

                    # added tax to total tax
                    cal_total_tax += this_item_tax
                    print(f_price, this_item_tax)
                    item_dict = {
                        "type": "physical",
                        "reference": f'{i.unit.sku}',
                        "name": f'{i.unit.kitchen} with {i.unit}',
                        "quantity": i.qty,
                        "quantity_unit": "pcs",
                        "unit_price": int(i.unit.price + (i.unit.price * 20 / 100)) * 100,
                        "tax_rate": 2000,
                        "total_amount": f_price,
                        "total_discount_amount": 0,
                        "total_tax_amount": this_item_tax
                    }
                    raw_data['order_lines'].append(item_dict)
                    price += int((i.unit.price + (i.unit.price * 20 / 100)) * i.qty)
            else:
                sample_price += 5
                # total amount
                f_price = int(5 * 100)

                # total tax
                this_item_tax = int(((f_price * 10000) / (10000 + 1000)) / 10)

                # added tax to total tax
                cal_total_tax += this_item_tax
                item_dict = {
                    "type": "physical",
                    "reference": 'Sample',
                    "name": f'{item.kitchen_order.kitchen} Sample',
                    "quantity": 1,
                    "quantity_unit": "pcs",
                    "unit_price": f_price,
                    "tax_rate": 1000,
                    "total_amount": f_price,
                    "total_discount_amount": 0,
                    "total_tax_amount": this_item_tax
                }
                raw_data['order_lines'].append(item_dict)

        if item.service:
            service = 'service'
            sample_price += 50
            # total amount
            f_price = 50 * 100

            # total tax
            this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)

            # added tax to total tax
            cal_total_tax += this_item_tax
            item_dict = {
                "type": "physical",
                "reference": "19-402-USA",
                "name": 'Service',
                "quantity": 1,
                "quantity_unit": "pcs",
                "unit_price": 50 * 100,
                "tax_rate": 2000,
                "total_amount": 50 * 100,
                "total_discount_amount": 0,
                "total_tax_amount": this_item_tax
            }
            raw_data['order_lines'].append(item_dict)
    if price < 300 and price != 0:
        raw_data['shipping_options'] = [{
            'id': 'Shipping Detail',
            'name': 'Shipping',
            'price': 3000,
            'preselected': True,
            'tax_rate': 0,
            'tax_amount': 0
        }, ]
    price = int(price + sample_price)
    raw_data['order_amount'] = price * 100
    raw_data['order_tax_amount'] = cal_total_tax

    data = json.dumps(raw_data)
    value = json.dumps({
        'PK34671_2300d5bebae2': 'wPTKWhc1xSyImu6R'
    })

    headers = {'Authorization': 'Basic UEszNDY3MV8yMzAwZDViZWJhZTI6d1BUS1doYzF4U3lJbXU2Ug==',
               'content-type': 'application/json'
               }

    res = requests.post(url, data=data, headers=headers)
    result = res.json()
    ctx = {'html': result['html_snippet'],'cart_count':cart_count(request),'appliances': appliances, 'worktop': worktop}
    request.session['order_id'] = result['order_id']
    return render(request, 'klarna_snippet.html', ctx)


def confirmation(request):
    base_url = 'https://api.playground.klarna.com'
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    order_id = request.session.get('order_id')
    url = base_url + f'/checkout/v3/orders/{order_id}'
    headers = {'Authorization': 'Basic UEszNDY3MV8yMzAwZDViZWJhZTI6d1BUS1doYzF4U3lJbXU2Ug==',
               'content-type': 'application/json'
               }
    res = requests.get(url, headers=headers)
    result = res.json()
    ctx = {'html': result['html_snippet'],'cart_count':cart_count(request),'appliances': appliances, 'worktop': worktop}
    acknowledge_url = base_url + f'/ordermanagement/v1/orders/{order_id}/acknowledge'
    requests.post(acknowledge_url, headers=headers)
    send_mail(
        'Push',
        'An order has been placed. Kindly check your klarna account to process the order.',
        None,
        ['hiphop.ali1041@gmail.com']
    )
    info = UserInfo.objects.get(pk=request.session.get('user_info_pk'))
    complete_order = CompleteOrder.objects.create(user=info)
    my_cart = Cart.objects.select_related('user').filter(user=request.user,checkedout=False)
    # print(my_cart.checkedout,my_cart)
    complete_order.order.add(*my_cart)
    Cart.objects.filter(user=request.user, checkedout=False).update(checkedout=True)
    return render(request, 'klarna_confirm.html', ctx)


def push(request, **kwargs):
    if request.method == 'POST':
        print(request.POST)
        send_mail(
            'Push',
            'Your push order',
            None,
            ['hiphop.ali1041@gmail.com']
        )
    raise ValueError('Push notification through klarna')
    return redirect('application:index')
