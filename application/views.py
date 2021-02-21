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
# import base64
from django.core.mail import send_mail, EmailMultiAlternatives,send_mass_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from datetime import datetime, timezone, time

# Create your views here.
User = get_user_model()


def meta_info(page):
    return MetaInfo.objects.first()


def async_task():
    now = datetime.now(tz=timezone.utc)
    all_carts = Cart.objects.select_related('user').all()
    all_user_email_list = []
    for time1 in all_carts:
        # print(now.hour,time1.date.hour)
        first_value = now.hour
        second_value = time1.date.hour
        if second_value>first_value:
            first_value+=24

        x = first_value-second_value
        # print(x)

        y = x
        # print(y / 10 == int(y / 10))
        if (y == 10 or y / 10 == int(y/10)) and x!=0:
            # print(time1.user,time1.user.email)
            all_user_email_list.append(time1.user.email)

    dup_removed_emails = list(set(all_user_email_list))
    if dup_removed_emails:
        email_tuple = (
            'Items in the cart are waiting!!',
            'This is a reminder email. Your items in the cart are waiting. Visit the site and checkout right away.',
            None,
            dup_removed_emails
        )
        send_mass_mail((email_tuple,),fail_silently=False


        )

    send_mail(
        'to check',
        f'email to {dup_removed_emails}',
        None,
        ['hiphop.ali1041@gmail.com']
    )


def cart_count(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {'Count': Cart.objects.select_related('user').filter(user=request.user, checkedout=False).count()})
    else:
        return JsonResponse({'Count': 0})


def email_send(email, to):
    html_content = ''
    subject = ''
    if to == 'newsletter':
        html_content = render_to_string('inc/newsleter.html')
        subject = 'THANK YOU FOR SUBSCRIBING!'
    elif to == 'order':
        html_content = render_to_string('inc/order_email.html')
        subject = 'Your order is being processed'
    elif to == 'register':
        html_content = render_to_string('inc/email.html')
        subject = 'Thank you for registering with TKC Kitchens'
    elif to == 'install':
        html_content = render_to_string('inc/instal_email.html')
        subject = 'Thank you for Contacting TKC Kitchens'
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        None,
        [email],
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


mylist = []


def signup(request):
    if request.method == 'GET':
        redirect_to = request.META.get('HTTP_REFERER')
        if not redirect_to == 'https://tkc-kitchen.nw.r.appspot.com/login/':
            if not mylist:
                mylist.append(redirect_to)

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
            messages.warning(request, 'This username is taken. Enter a different one.')
            return redirect('application:signup')
        user.set_password(pas1)
        user.save()
        email_send(user.email, 'register')
        msg = messages.success(request, "You've registered successfully. Please Login to view prices & latest offers.")
        return redirect('application:login')
    return render(request, 'signup.html')


def my_redirect(url):
    mylist.append(url)
    return mylist


def login(request):
    redirect_to = request.META.get('HTTP_REFERER')
    if request.method == 'GET':
        my_redirect(redirect_to)
    if request.method == 'POST':
        try:
            get_username = User.objects.get(email=request.POST['email'])
        except:
            messages.warning(request, 'Invalid email or password')
            return redirect('application:login')
        user = authenticate(username=get_username.username, password=request.POST['password'])
        if user is not None:
            abs_uri = request.get_host()
            log(request, user)
            new_list = mylist.copy()
            x = new_list[0]

            mylist.clear()
            if x == f"http://{abs_uri}/login/" or x == f"http://{abs_uri}/signup/" or x == f'http://{abs_uri}/password_reset_done/':
                return redirect('application:index')
            return redirect(x)
        else:
            messages.warning(request, 'Enter a valid username or password!!')
            return redirect('application:login')

    ctx = {'url': redirect_to}
    ctx['worktop'] = Worktop_category.objects.all()
    ctx['appliances'] = Category_Applianes.objects.all()
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']
    return render(request, 'registration/login.html', ctx)


def index(request):
    user_cart = cart_count(request)
    meta = meta_info('home')
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'blogs': Blogs.objects.all()[:3], 'cart_count': json.loads(user_cart.content)['Count'],
           'appliances': appliances, 'worktop': worktop, 'name': meta.home_name
        , 'description': meta.home_description, 'title': meta.home_title}

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
    template_name = 'new_kitchen_style.html'
    context_object_name = 'list'

    def get_context_data(self, *args, **kwargs):
        ctx = super(AllKitchenView, self).get_context_data(*args, **kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        count = cart_count(self.request)
        ctx['cart_count'] = json.loads(count.content)['Count']
        meta = meta_info('home')
        ctx['name'] = meta.kitchen_name
        ctx['description'] = meta.kitchen_description
        ctx['title'] = meta.kitchen_title
        return ctx

    def get_queryset(self):
        kitchens = Kitchen.objects.select_related('kitchen_type').filter(available=True)
        all_unique = kitchens.values('color').annotate(count=Count('color')).order_by()
        colors = [i['color'] for i in all_unique]
        return colors


# ajax kitchen request

def get_kitchen(request, **kwargs):
    kitchens = Kitchen.objects.select_related('kitchen_type').filter(color=kwargs['color'], available=True)
    serialize_kitchens = serialize('json', kitchens, use_natural_foreign_keys=True)
    return JsonResponse({'kitchens': serialize_kitchens}, safe=False)


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
        ctx['kitchen_view'] = KitchenCategory.objects.get(name__iexact=self.kwargs['name'])
        ctx['search'] = UnitType.objects.all()
        count = cart_count(self.request)
        ctx['cart_count'] = json.loads(count.content)['Count']
        if 'vero' in ctx['kitchen_view'].name:
            ctx['form'] = 'form'
        ctx['kitchen_color'] = Kitchen.objects.select_related('kitchen_type').filter(kitchen_type=ctx['kitchen_view'])
        ctx['current_color'] = self.kwargs['color']
        ctx['current_pic'] = Kitchen.objects.select_related('kitchen_type').get(color=self.kwargs['color'],
                                                                                kitchen_type=ctx['kitchen_view'])
        return ctx

    def get_queryset(self):
        kitchen_view = KitchenCategory.objects.get(name__iexact=self.kwargs['name'])

        units = Units.objects.select_related('kitchen', 'unit_type').filter(kitchen=kitchen_view, available=True)
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
        qs = WorkTop.objects.select_related('category').filter(category=category, available=True)
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
        count = cart_count(self.request)
        ctx['cart_count'] = json.loads(count.content)['Count']

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
        meta = meta_info('home')
        ctx['name'] = meta.worktop_name
        ctx['description'] = meta.worktop_description
        ctx['title'] = meta.worktop_title
        ctx['product'] = 'worktop'
        return ctx


# random queryset
def random_queryset():
    one = list(WorkTop.objects.all())
    random_sample = random.sample(one, 2)
    three = list(Appliances.objects.all())
    random_sample_2 = random.sample(three, 2)
    return random_sample, random_sample_2


# worktop detail
class WorktopDetailView(generic.DetailView):
    model = WorkTop
    template_name = 'worktop_app_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(WorktopDetailView, self).get_context_data(**kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        count = cart_count(self.request)
        ctx['cart_count'] = json.loads(count.content)['Count']
        ctx['feature1'] = random_queryset()[0]
        ctx['feature2'] = random_queryset()[1]
        if self.kwargs['name'] == 'worktop':
            ctx['product'] = 'worktop'
            ctx['review'] = Review.objects.select_related('worktop').filter(worktop_id=self.kwargs['pk'],
                                                                            approval='Approved')
            meta = meta_info('home')
            ctx['name'] = meta.worktop_name
            ctx['description'] = meta.worktop_description
            ctx['title'] = meta.worktop_title
        elif self.kwargs['name'] == 'appliance':
            ctx['product'] = 'appliance'
            ctx['review'] = Review.objects.select_related('appliances').filter(appliances_id=self.kwargs['pk'],
                                                                               approval='Approved')
            meta = meta_info('home')
            ctx['name'] = meta.appliance_name
            ctx['description'] = meta.appliance_description
            ctx['title'] = meta.appliance_title
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

    def get_queryset(self):
        category = Category_Applianes.objects.get(pk=self.kwargs['pk'])
        x = Appliances.objects.select_related('category').filter(category=category, available=True)
        filters = AppliancesFilters(self.request.GET, queryset=x)
        if len(self.request.GET) != 0:
            x = filters.qs
        return x

    def get_context_data(self, *args, **kwargs):
        ctx = super(AppliancesListView, self).get_context_data(*args, **kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        count = cart_count(self.request)
        ctx['cart_count'] = json.loads(count.content)['Count']

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
        # filters = AppliancesFilters(self.request.GET, queryset=Appliances.objects.select_related('category').all())
        # ctx['search'] = filters
        ctx['product'] = 'appliance'
        meta = meta_info('home')
        ctx['name'] = meta.appliance_name
        ctx['description'] = meta.appliance_description
        ctx['title'] = meta.appliance_title
        return ctx


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
                my_cart = Cart.objects.get(user=request.user, worktop=worktop, checkedout=False)
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
                my_cart = Cart.objects.get(user=request.user, appliances=appliance, checkedout=False)
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
            print(color, name, qty)
            # try:
            kitchen = Kitchen.objects.select_related('kitchen_type').get(
                kitchen_type=KitchenCategory.objects.get(name__iexact=name), color__iexact=color)
            # except:
            #     pass
            # cat = KitchenCategory.objects.get(name__iexact=kwargs['name'])
            # return redirect(reverse_lazy('application:kitchen-view', kwargs={'pk': cat.pk}))
            unit = Units.objects.select_related('kitchen').get(pk=kwargs['pk'])

            pre_order = Combining.objects.select_related('kitchen').filter(user=request.user, kitchen=kitchen)
            if pre_order:
                already_exist = Units_intermediate.objects.select_related('unit', 'combine').filter(unit_id=unit.pk)
                if already_exist:
                    already_exist[0].qty = qty + already_exist[0].qty
                    already_exist[0].save()
                else:
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
            my_cart = Cart.objects.select_related('user', 'appliances').get(user=request.user, checkedout=False,
                                                                            appliances=appliance)
            my_cart.qty = kwargs['qty']
            my_cart.save()
            return JsonResponse({'update': 'update'})

        elif kwargs['product'] == 'worktop':
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.select_related('worktop', 'user').get(user=request.user, worktop=worktop,
                                                                         checkedout=False)
            my_cart.qty = kwargs['qty']
            my_cart.save()
            return JsonResponse({'update': 'update'})

    elif kwargs['process'] == 'delete':
        if kwargs['product'] == 'worktop':
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.filter(worktop_id=worktop.pk, checkedout=False)
            my_cart.delete()
            return JsonResponse({'removed': 'removed'})

        elif kwargs['product'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            my_cart = Cart.objects.filter(appliances_id=appliance.pk, checkedout=False)
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
    cart = Cart.objects.select_related('kitchen_order', 'appliances', 'worktop', 'user').filter(user=request.user,
                                                                                                checkedout=False)
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
           'feature2': random_queryset()[1]}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']
    return render(request, 'cart.html', ctx)


# contact form page
def contact(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    if request.method == 'POST':
        messages.info(request,
                      'An email with your given info was sent to one of our customer care representative. We will contact you as soon as possible.')
        contact_instance = ContactActual.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            order_number=request.POST['order'],
            detail=request.POST['detail'],
            reason=request.POST.getlist('check1')
        )
        html_content = render_to_string('inc/my_contact.html',{'detail':contact_instance})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            'Contact form',
            text_content,
            None,
            ['service@tkckitchens.co.uk']
        )
        email.attach_alternative(html_content,'text/html')
        email.send()
        return redirect('application:contact')
    meta = meta_info('home')
    ctx = {'appliances': appliances, 'worktop': worktop, 'cart_count': cart_count(request),
           'name': meta.contact_name
        , 'description': meta.contact_description, 'title': meta.contact_title
           }
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']
    return render(request, 'contact_us.html', ctx)


# installation page
def installation(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    meta = meta_info('home')

    ctx = {'appliances': appliances, 'worktop': worktop, 'name': meta.install_name
        , 'description': meta.install_description, 'title': meta.install_title
           }
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']

    return render(request, 'inc/installation.html', ctx)


# design page
def design(request):
    worktop = Worktop_category.objects.all()
    meta = meta_info('home')
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop,
           'name': meta.design_name
        , 'description': meta.design_description, 'title': meta.design_title
           }
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']

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
        count = cart_count(request)
        ctx['cart_count'] = json.loads(count.content)['Count']

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
        count = cart_count(request)
        ctx['cart_count'] = json.loads(count.content)['Count']

        return render(request, 'search.html', ctx)


class BlogList(generic.ListView):
    model = Blogs
    template_name = 'blog.html'
    context_object_name = 'list'

    def get_context_data(self, **kwargs):
        ctx = super(BlogList, self).get_context_data(**kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        count = cart_count(self.request)
        ctx['cart_count'] = json.loads(count.content)['Count']

        return ctx


class BlogDetail(generic.DetailView):
    model = Blogs
    template_name = 'blog_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(BlogDetail, self).get_context_data(**kwargs)
        ctx['worktop'] = Worktop_category.objects.all()
        ctx['appliances'] = Category_Applianes.objects.all()
        count = cart_count(self.request)
        ctx['cart_count'] = json.loads(count.content)['Count']

        return ctx


def newsletter(request):
    if request.body:
        data = json.loads(request.body)
        already_exist = Newsletter.objects.filter(email=data['email'])
        if already_exist:
            return JsonResponse({'added': 'not added'})
        Newsletter.objects.create(email=data['email'])
        email_send(data['email'], 'newsletter')
        return JsonResponse({'added': 'added'})


def terms(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']

    return render(request, 'TERMS OF SERVICE 5 (40).html', ctx)


def disclaimer(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']

    return render(request, 'Disclaimer1 (37).html', ctx)


def cancel(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']

    return render(request, 'CANCELLATION POLICY (16).html', ctx)


def intellectual(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']

    return render(request, 'Intellectual Property Notification (8).html', ctx)


def Gdp(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']

    return render(request, 'GDPR Privacy Policy2 (44).html', ctx)


def FAQ(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']
    return render(request, 'FAQ.html', ctx)


def Return(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']
    return render(request, 'Return and Refund Policy (2) (6).html', ctx)


def ship(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']

    return render(request, 'Shipping and Delivery Policy 1 (22).html', ctx)


def cook(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    ctx = {'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']

    return render(request, 'Cookies Policy3 (42).html', ctx)


def install_contact(request):
    worktop = Worktop_category.objects.all()
    appliances = Category_Applianes.objects.all()
    if request.method == 'POST':
        details = f"{request.POST['detail']} from the {request.META.get('HTTP_REFERER')}"
        contact_instance = ContactUs.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            site_address=request.POST['address'],
            detail=details,
            room_ready=request.POST['measure'],
            remove_old_kitchen=request.POST['old'],
            require_things=request.POST['ee'],
            your_budgets=request.POST['price'],

        )
        email_send(request.POST['email'], 'install')
        html_content = render_to_string('inc/my_install_email.html',{'detail':contact_instance})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            'Installation Service',
            text_content,
            None,
            ['service@tkckitchens.co.uk']
        )
        email.attach_alternative(html_content,'text/html')
        email.send()
        messages.info(request,
                      'Your form has been submitted. One of our customer care representative will contact you soon!')
        return redirect(request.META.get('HTTP_REFERER'))

    ctx = {'appliances': appliances, 'worktop': worktop, 'cart_count': cart_count(request)}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']
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
                door_number=data['door_number'],
                street_name=data['street_name'],
                city=data['city'],
                # region=data['region'],
                postcode=data['postcode'],
                country=data['country'],
            )
            request.session['user_info_pk'] = info.pk
            return redirect('application:create-order')
    ctx = {'form': form, 'appliances': appliances, 'worktop': worktop}
    count = cart_count(request)
    ctx['cart_count'] = json.loads(count.content)['Count']
    myuser = User.objects.get(username=request.user)
    ctx['email'] = myuser.email
    return render(request, 'checkout.html', ctx)


def temp_checkout(request, **kwargs):
    info = UserInfo.objects.get(pk=request.session.get('user_info_pk'))
    complete_order = CompleteOrder.objects.create(user=info)
    my_cart = Cart.objects.select_related('user').filter(user=request.user, checkedout=False)
    # print(my_cart.checkedout,my_cart)
    complete_order.order.add(*my_cart)
    Cart.objects.filter(user=request.user, checkedout=False).update(checkedout=True)
    email_send(info.email_address, 'order')
    count = cart_count(request)
    ctx = {'cart_count': json.loads(count.content)['Count']}
    ctx['worktop'] = Worktop_category.objects.all()
    ctx['appliances'] = Category_Applianes.objects.all()
    return render(request, 'temp_checkout.html', ctx)

# def create_order_klarna(request, **kwargs):
#     worktop = Worktop_category.objects.all()
#     appliances = Category_Applianes.objects.all()
#     base_url = 'https://api.playground.klarna.com'
#     url = base_url + '/checkout/v3/orders'
#
#     my_items = Cart.objects.select_related('kitchen_order', 'worktop', 'appliances', 'user').filter(user=request.user)
#     raw_data = {
#         "purchase_country": "GB",
#         "purchase_currency": "GBP",
#         "locale": "en-GB",
#         "order_amount": 0,
#         "order_tax_amount": 0,
#         "order_lines": [
#
#         ],
#         "merchant_urls": {
#             "terms": "https://www.example.com/terms.html",
#             "checkout": "https://www.example.com/checkout.html?order_id={checkout.order.id}",
#             "confirmation": "http://127.0.0.1:8000/order-confirmed/",
#             "push": "http://127.0.0.1:8000/push-email/",
#         },
#     }
#
#     price = 0
#     sample_price = 0
#     cal_total_tax = 0
#     for item in my_items:
#         if item.worktop:
#             if item.sample_worktop == 'Yes':
#                 sample_price += 5
#                 # total amount
#                 f_price = 5 * 100
#
#                 # total tax
#                 this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)
#
#                 # added tax to total tax
#                 cal_total_tax += this_item_tax
#                 item_dict = {
#                     "type": "physical",
#                     "reference": "19-402-USA",
#                     "name": f'{item.worktop.name} Sample',
#                     "quantity": item.qty,
#                     "quantity_unit": "pcs",
#                     "unit_price": f_price,
#                     "tax_rate": 2000,
#                     "total_amount": f_price,
#                     "total_discount_amount": 0,
#                     "total_tax_amount": this_item_tax
#                 }
#                 raw_data['order_lines'].append(item_dict)
#             else:
#                 # total amount
#                 f_price = int(item.worktop.price * item.qty * 100)
#
#                 # total tax
#                 this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)
#
#                 # added tax to total tax
#                 cal_total_tax += this_item_tax
#                 price += item.worktop.price * item.qty
#                 item_dict = {
#                     "type": "physical",
#                     "reference": "19-402-USA",
#                     "name": f'{item.worktop.name}',
#                     "quantity": item.qty,
#                     "quantity_unit": "pcs",
#                     "unit_price": int(item.worktop.price * 100),
#                     "tax_rate": 2000,
#                     "total_amount": f_price,
#                     "total_discount_amount": 0,
#                     "total_tax_amount": this_item_tax
#                 }
#                 raw_data['order_lines'].append(item_dict)
#         if item.appliances:
#             price += item.appliances.price * item.qty
#
#             # total amount
#             f_price = int(item.appliances.price * item.qty * 100)
#
#             # total tax
#             this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)
#
#             # added tax to total tax
#             cal_total_tax += this_item_tax
#             item_dict = {
#                 "type": "physical",
#                 "reference": "19-402-USA",
#                 "name": f'{item.appliances.name}',
#                 "quantity": item.qty,
#                 "quantity_unit": "pcs",
#                 "unit_price": int(item.appliances.price * 100),
#                 "tax_rate": 2000,
#                 "total_amount": f_price,
#                 "total_discount_amount": 0,
#                 "total_tax_amount": this_item_tax
#             }
#             raw_data['order_lines'].append(item_dict)
#         if item.kitchen_order:
#             if item.kitchen_order.units_intermediate_set.all():
#                 for i in item.kitchen_order.units_intermediate_set.all():
#                     # total amount
#                     f_price = int(int(i.unit.price + (i.unit.price * 20 / 100)) * i.qty * 100)
#                     # separate_tax = f_price*20/100
#                     # print(separate_tax)
#                     #
#                     # f_price = int(f_price+separate_tax)
#                     # total tax
#                     this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)
#
#                     # tax cal
#                     # f_price = f_price+this_item_tax
#
#                     # added tax to total tax
#                     cal_total_tax += this_item_tax
#                     print(f_price, this_item_tax)
#                     item_dict = {
#                         "type": "physical",
#                         "reference": f'{i.unit.sku}',
#                         "name": f'{i.unit.kitchen} with {i.unit}',
#                         "quantity": i.qty,
#                         "quantity_unit": "pcs",
#                         "unit_price": int(i.unit.price + (i.unit.price * 20 / 100)) * 100,
#                         "tax_rate": 2000,
#                         "total_amount": f_price,
#                         "total_discount_amount": 0,
#                         "total_tax_amount": this_item_tax
#                     }
#                     raw_data['order_lines'].append(item_dict)
#                     price += int((i.unit.price + (i.unit.price * 20 / 100)) * i.qty)
#             else:
#                 sample_price += 5
#                 # total amount
#                 f_price = int(5 * 100)
#
#                 # total tax
#                 this_item_tax = int(((f_price * 10000) / (10000 + 1000)) / 10)
#
#                 # added tax to total tax
#                 cal_total_tax += this_item_tax
#                 item_dict = {
#                     "type": "physical",
#                     "reference": 'Sample',
#                     "name": f'{item.kitchen_order.kitchen} Sample',
#                     "quantity": 1,
#                     "quantity_unit": "pcs",
#                     "unit_price": f_price,
#                     "tax_rate": 1000,
#                     "total_amount": f_price,
#                     "total_discount_amount": 0,
#                     "total_tax_amount": this_item_tax
#                 }
#                 raw_data['order_lines'].append(item_dict)
#
#         if item.service:
#             service = 'service'
#             sample_price += 50
#             # total amount
#             f_price = 50 * 100
#
#             # total tax
#             this_item_tax = int((((f_price * 10000) / (10000 + 2000)) / 10) * 2)
#
#             # added tax to total tax
#             cal_total_tax += this_item_tax
#             item_dict = {
#                 "type": "physical",
#                 "reference": "19-402-USA",
#                 "name": 'Service',
#                 "quantity": 1,
#                 "quantity_unit": "pcs",
#                 "unit_price": 50 * 100,
#                 "tax_rate": 2000,
#                 "total_amount": 50 * 100,
#                 "total_discount_amount": 0,
#                 "total_tax_amount": this_item_tax
#             }
#             raw_data['order_lines'].append(item_dict)
#     if price < 300 and price != 0:
#         raw_data['shipping_options'] = [{
#             'id': 'Shipping Detail',
#             'name': 'Shipping',
#             'price': 3000,
#             'preselected': True,
#             'tax_rate': 0,
#             'tax_amount': 0
#         }, ]
#     price = int(price + sample_price)
#     raw_data['order_amount'] = price * 100
#     raw_data['order_tax_amount'] = cal_total_tax
#
#     data = json.dumps(raw_data)
#     value = json.dumps({
#         'PK34671_2300d5bebae2': 'wPTKWhc1xSyImu6R'
#     })
#
#     headers = {'Authorization': 'Basic UEszNDY3MV8yMzAwZDViZWJhZTI6d1BUS1doYzF4U3lJbXU2Ug==',
#                'content-type': 'application/json'
#                }
#
#     res = requests.post(url, data=data, headers=headers)
#     result = res.json()
#     ctx = {'html': result['html_snippet'], 'cart_count': cart_count(request), 'appliances': appliances,
#            'worktop': worktop}
#     request.session['order_id'] = result['order_id']
#     return render(request, 'klarna_snippet.html', ctx)
#
#
# def confirmation(request):
#     base_url = 'https://api.playground.klarna.com'
#     worktop = Worktop_category.objects.all()
#     appliances = Category_Applianes.objects.all()
#     order_id = request.session.get('order_id')
#     url = base_url + f'/checkout/v3/orders/{order_id}'
#     headers = {'Authorization': 'Basic UEszNDY3MV8yMzAwZDViZWJhZTI6d1BUS1doYzF4U3lJbXU2Ug==',
#                'content-type': 'application/json'
#                }
#     res = requests.get(url, headers=headers)
#     result = res.json()
#     ctx = {'html': result['html_snippet'], 'cart_count': cart_count(request), 'appliances': appliances,
#            'worktop': worktop}
#     acknowledge_url = base_url + f'/ordermanagement/v1/orders/{order_id}/acknowledge'
#     requests.post(acknowledge_url, headers=headers)
#     send_mail(
#         'Push',
#         'An order has been placed. Kindly check your klarna account to process the order.',
#         None,
#         ['hiphop.ali1041@gmail.com']
#     )
#     info = UserInfo.objects.get(pk=request.session.get('user_info_pk'))
#     complete_order = CompleteOrder.objects.create(user=info)
#     my_cart = Cart.objects.select_related('user').filter(user=request.user, checkedout=False)
#     # print(my_cart.checkedout,my_cart)
#     complete_order.order.add(*my_cart)
#     Cart.objects.filter(user=request.user, checkedout=False).update(checkedout=True)
#     return render(request, 'klarna_confirm.html', ctx)
