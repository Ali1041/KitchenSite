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
# import klarnacheckout
# import requests
# import base64
from django.core.mail import send_mail, EmailMultiAlternatives, send_mass_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from datetime import datetime, timezone, time
from django import template
from django.conf import settings

# Create your views here.
User = get_user_model()
register = template.Library()


# custom error handling pages
# 403 error page
def error_403(request, exception):
    return render(request, '403.html')


# 404 error page
def error_404(request, exception):
    if 'adminPanel' in request.META.get('HTTP_REFERER'):
        error_403(request, exception)

    return render(request, '403.html')


# 500 error page
def error_500(request):
    return render(request, '404.html')


# meta info on pages provided here
def meta_info(page):
    return MetaStatic.objects.first()


# async taks of sending emails
def async_task():
    now = datetime.now(tz=timezone.utc)
    all_carts = Cart.objects.select_related('user').all()
    all_user_email_list = []
    for time1 in all_carts:
        first_value = now.hour
        second_value = time1.date.hour
        if second_value > first_value:
            first_value += 24

        x = first_value - second_value

        y = x
        if (y == 72 or y / 72 == int(y / 72)) and x != 0:
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
        send_mass_mail((email_tuple,), fail_silently=True

                       )

    # send_mail(
    #     'to check',
    #     f'email to {dup_removed_emails}',
    #     None,
    #     ['hiphop.ali1041@gmail.com']
    # )


# counting of cart items
def cart_count(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {'Count': Cart.objects.select_related('user').filter(user=request.user, checkedout=False).count()})
    else:
        return JsonResponse({'Count': 0})


# sending emails on different actions
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


# random queryset
def random_queryset():
    one = list(WorkTop.objects.all())
    random_sample = random.sample(one, 2)
    three = list(Appliances.objects.all())
    random_sample_2 = random.sample(three, 2)
    return random_sample, random_sample_2


# sign up view
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
        messages.success(request, "You've registered successfully. Please Login to view prices & latest offers.")
        return redirect('application:login')
    meta = meta_info('home')
    ctx = {'name': meta.signup_name
        , 'description': meta.signup_description, 'title': meta.signup_title}
    return render(request, 'signup.html', ctx)


def my_redirect(url):
    mylist.append(url)
    return mylist


# login view
def login(request):
    if request.method == 'GET':
        redirect_to = request.META.get('HTTP_REFERER')
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
            if len(mylist) == 0:
                return redirect('application:index')
            if mylist[0] is None:
                return redirect('application:index')
            new_list = mylist.copy()
            mylist.clear()
            x = new_list[-1]

            if x == f"http://{abs_uri}/login/" or x == f"http://{abs_uri}/signup/" or x == f'http://{abs_uri}/password_reset_done/':
                return redirect('application:index')
            return redirect(x)
        else:
            messages.warning(request, 'Enter a valid username or password!!')
            return redirect('application:login')

    meta = meta_info('home')
    ctx = {'name': meta.login_name
        , 'description': meta.login_description, 'title': meta.login_title}
    return render(request, 'registration/login.html', ctx)


# home page
def index(request):
    if request.method == 'POST':
        Brochure.objects.create(
            first_name=request.POST['first'],
            last_name=request.POST['last'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            detail=request.POST['detail']
        )
        html_content = render_to_string('inc/brochure_email.html')
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            'YOUR BROCHURE',
            text_content,
            None,
            [request.POST['email'], 'kashif@tkckitchens.co.uk']
        )
        email.attach_alternative(html_content, 'text/html')
        email.send()
        messages.success(request, 'Your brochure has been sent successfully!!')
        return redirect('application:index')

    meta = meta_info('home')
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')

    ctx = {'blog': Blogs.objects.all()[:3],
           'name': meta.home_name
        , 'description': meta.home_description, 'title': meta.home_title, 'vapid_key': vapid_key, 'user': request.user}

    return render(request, 'base.html', ctx)


# accessories list

class AccessoriesList(generic.ListView):
    model = Accessories
    template_name = 'accessories_list.html'
    context_object_name = 'list'
    paginate_by = 10

    def get_queryset(self):
        ctx = Accessories.objects.select_related('accessories_type').filter(
            accessories_type__slug__iexact=self.kwargs['slug'])

        if len(self.request.GET) > 1:
            filter_result = AccessoriesFilter(self.request.GET,
                                              queryset=Accessories.objects.select_related('accessories_type').filter(
                                                  accessories_type__slug__iexact=self.kwargs['slug']))
            ctx = filter_result.qs
        return ctx


# accessories detail
class AccessoriesDetail(generic.DetailView):
    model = Accessories
    template_name = 'accessories_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(AccessoriesDetail, self).get_context_data(**kwargs)
        ctx['feature1'] = random_queryset()[0]
        ctx['feature2'] = random_queryset()[1]
        ctx['product'] = 'accessories'
        ctx['review'] = Review.objects.select_related('accessories').filter(accessories_id=self.kwargs['pk'],
                                                                            approval='Approved')

        return ctx

    def get_queryset(self):
        return Accessories.objects.select_related('accessories_type').filter(
            pk=self.kwargs['pk'])


# all kitchen
class AllKitchenView(generic.ListView):
    model = Kitchen
    template_name = 'new_kitchen_style.html'
    context_object_name = 'list'

    def get_context_data(self, *args, **kwargs):
        ctx = super(AllKitchenView, self).get_context_data(*args, **kwargs)
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
    kitchens = Kitchen.objects.select_related('kitchen_type').all()
    annotated_kitchen = kitchens.values('kitchen_type__name').annotate(count=Count('kitchen_type')).order_by()
    my_list = []
    for i in [1, 2, 6, 7, 8, 9, 3, 4, 0, 5]:
        my_list.append(annotated_kitchen[i])
    for i in range(10, annotated_kitchen.count()):
        my_list.append(annotated_kitchen[i])
    list_dict = []
    for item in my_list:
        x = Kitchen.objects.select_related('kitchen_type').filter(kitchen_type__name=item['kitchen_type__name'],
                                                                  available=True)
        annotated_color = x.values('color', 'kitchen_type__name').annotate(count=Count('color')).order_by()
        inner_dict = {'name': item['kitchen_type__name'], 'description': x[0].description}

        color_list = []
        imgs_list = []
        for i in annotated_color:
            color_list.append(i['color'])
            img_color = Kitchen.objects.select_related('kitchen_type').filter(
                kitchen_type__name=i['kitchen_type__name'], color=i['color'], available=True)
            imgs_list.append(img_color[0].img)
        inner_dict['colors'] = color_list
        inner_dict['imgs'] = imgs_list
        list_dict.append(inner_dict)

    ctx = {'list': list_dict}

    meta = meta_info('home')
    ctx['name'] = meta.kitchen_name
    ctx['title'] = meta.kitchen_title
    ctx['description'] = meta.kitchen_description
    return render(request, 'all_kitchen.html', ctx)


# view for kitchen display
class KitchenView(generic.ListView):
    model = Units
    paginate_by = 10
    template_name = 'kitchen.html'
    context_object_name = 'units'

    def get_context_data(self, *args, **kwargs):
        ctx = super(KitchenView, self).get_context_data(*args, **kwargs)

        # actual functionality
        color = self.kwargs['color']
        if len(self.kwargs['color'].split("'")) > 1:
            color = self.kwargs['color'].split("'")[1]
        ctx['kitchen_view'] = KitchenCategory.objects.get(name__iexact=self.kwargs['name'])
        ctx['search'] = UnitType.objects.all()

        if 'vero' in str(ctx['kitchen_view'].name):
            ctx['form'] = 'form'
        all_colors = Kitchen.objects.select_related('kitchen_type').filter(
            kitchen_type=ctx['kitchen_view'], available=True)
        ctx['kitchen_color'] = all_colors.values('color').annotate(count=Count('color')).order_by()
        ctx['current_color'] = color
        ctx['current_kitchen'] = Kitchen.objects.select_related('kitchen_type').filter(
            kitchen_type=ctx['kitchen_view'], color=color, available=True
        )

        return ctx

    def get_queryset(self):
        kitchen_view = KitchenCategory.objects.get(name__iexact=self.kwargs['name'])
        if len(self.kwargs) == 3:
            return Units.objects.select_related('kitchen', 'unit_type').filter(pk=self.kwargs['unit'], available=True)
        else:
            units = Units.objects.select_related('kitchen', 'unit_type').filter(kitchen=kitchen_view, available=True)
            filters = UnitFilter(self.request.GET,
                                 queryset=Units.objects.select_related('kitchen').filter(kitchen=kitchen_view))
            if len(self.request.GET) != 0:
                units = filters.qs
            return units


# AJAX units
def search_units(request, **kwargs):
    units_instances = Units.objects.filter(Q(name__icontains=kwargs.get('search'))
                                           | Q(description__icontains=kwargs.get('search')) |
                                           Q(unit_type__name__icontains=kwargs.get('search')),
                                           kitchen__name=kwargs['name'])
    if units_instances:
        serialized_instances = serialize('json', units_instances,
                                         fields=('pk', 'name', 'description', 'price', 'sku', 'img', 'unit_type')
                                         , use_natural_foreign_keys=True)
        return JsonResponse({'response': serialized_instances})
    else:
        return JsonResponse({'response': 'No results'})


# Worktop list
class WorktopListView(generic.ListView):
    model = WorkTop
    template_name = 'worktop.html'
    context_object_name = 'list'
    paginate_by = 10

    def get_queryset(self):
        category = Worktop_category.objects.get(slug=self.kwargs['slug'])
        qs = WorkTop.objects.select_related('category').filter(category=category, available=True)
        filters = WorktopFilters(self.request.GET, queryset=qs)
        if len(self.request.GET) != 0:
            qs = filters.qs
        if category.worktop_type == 'Stone Worktops':
            qs = ['stone', 'stone']
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super(WorktopListView, self).get_context_data(*args, **kwargs)

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
                    ctx['meta'] = Worktop_category.objects.get(worktop_type='Stone Worktops')

        ctx['product'] = 'worktop'
        return ctx


# worktop detail
class WorktopDetailView(generic.DetailView):
    model = WorkTop
    template_name = 'worktop_app_detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        ctx = super(WorktopDetailView, self).get_context_data(**kwargs)

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

    def get_queryset(self):
        category = Category_Applianes.objects.get(slug=self.kwargs['slug'])
        x = Appliances.objects.select_related('category').filter(category=category, available=True)
        filters = AppliancesFilters(self.request.GET, queryset=x)
        if len(self.request.GET) != 0:
            x = filters.qs
        return x

    def get_context_data(self, *args, **kwargs):
        ctx = super(AppliancesListView, self).get_context_data(*args, **kwargs)
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

        ctx['product'] = 'appliance'
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

        elif kwargs['product'] == 'accessories':
            accessory = Accessories.objects.select_related('accessories_type').get(pk=kwargs['pk'])
            try:
                my_cart = Cart.objects.get(user=request.user, accessories=accessory, checkedout=False)
                x = my_cart.qty
                my_cart.qty = x + kwargs['qty']
                my_cart.save()
            except:
                # accessories cart
                my_cart = Cart.objects.create(user=request.user, accessories=accessory, qty=kwargs['qty'])
            return JsonResponse({'add': 'added'})

        else:
            # kitchen cart
            color = kwargs['product']
            name = kwargs['name']
            qty = kwargs['qty']
            kitchen = Kitchen.objects.select_related('kitchen_type').get(
                kitchen_type=KitchenCategory.objects.get(name__iexact=name), color__iexact=color)

            unit = Units.objects.select_related('kitchen').get(pk=kwargs['pk'])
            pre_order = Combining.objects.select_related('kitchen').filter(user=request.user, kitchen=kitchen,
                                                                           kitchen__color=color, checkout=False)
            if pre_order:
                already_exist = Units_intermediate.objects.select_related('unit', 'combine').filter(unit_id=unit.pk)
                if already_exist:
                    already_exist[0].qty = qty
                    already_exist[0].save()
                else:
                    unit_inter = Units_intermediate.objects.create(unit=unit, qty=qty, combine=pre_order[0])
                    pre_order[0].save()
                    unit_inter.save()
            else:
                pre_order = Combining.objects.create(kitchen=kitchen, user=request.user, checkout=False)
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
        elif kwargs['product'] == 'accessories':
            accessory = Accessories.objects.select_related('accessories_type').get(pk=kwargs['pk'])
            my_cart = Cart.objects.select_related('accessories', 'user').get(user=request.user, accessories=accessory,
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

        elif kwargs['product'] == 'accessories':
            accessory = Accessories.objects.select_related('accessories_type').get(pk=kwargs['pk'])
            my_cart = Cart.objects.filter(user=request.user, accessories=accessory)
            my_cart.delete()
            return JsonResponse({'removed': 'removed'})

        else:
            intermediate_model = Combining.objects.get(pk=kwargs['pk'])
            intermediate_model.delete()
            return JsonResponse({'removed': 'removed'})


def cart(request):
    if not request.user.is_authenticated:
        return redirect('application:login')
    cart = Cart.objects.select_related('kitchen_order', 'appliances', 'worktop', 'user').filter(user=request.user,
                                                                                                checkedout=False)
    price = 0
    worktop_cart = []
    appliances_cart = []
    accessories_cart = []
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
        if item.accessories:
            VAT = (item.accessories.price * 20) / 100
            included_VAT = VAT + item.accessories.price
            price += included_VAT * item.qty
            accessories_cart.append(item)
        if item.kitchen_order:
            if item.kitchen_order.units_intermediate_set.all():
                for i in item.kitchen_order.units_intermediate_set.all():
                    VAT = (i.unit.price * 20) / 100
                    included_VAT = VAT + i.unit.price
                    price += included_VAT * i.qty
            else:
                sample_price += 4.99
        if item.service:
            service = 'service'
            sample_price += 0
            for_check2 = False
    if price < 300 and price != 0:
        price += 30
    price = price + sample_price

    ctx = {'cart': cart, 'service': service, 'accessories_cart': accessories_cart, 'worktop_cart': worktop_cart,
           'appliances_cart': appliances_cart,
           'total': price, 'feature1': random_queryset()[0],
           'feature2': random_queryset()[1]}

    return render(request, 'cart.html', ctx)


# contact form page
def contact(request):
    if request.method == 'POST':
        messages.info(request,
                      'An email with your given info was sent to one of our customer care representative. We will contact you as soon as possible.')
        detail_contact = f"{request.POST['detail']}/{datetime.now()} "
        order_number = 'N/A'
        if request.POST['order']:
            order_number = request.POST['order']
        contact_instance = ContactActual.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            order_number=order_number,
            detail=detail_contact,
            reason=request.POST.getlist('check1')
        )
        html_content = render_to_string('inc/my_contact.html', {'detail': contact_instance})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            'Contact form',
            text_content,
            None,
            ['service@tkckitchens.co.uk', 'kashif@tkckitchens.co.uk']
        )
        email.attach_alternative(html_content, 'text/html')
        email.send()
        return redirect('application:contact')
    meta = meta_info('home')
    ctx = {
        'name': meta.contact_name
        , 'description': meta.contact_description, 'title': meta.contact_title
    }

    return render(request, 'contact_us.html', ctx)


# installation page
def installation(request):
    meta = meta_info('home')

    ctx = {'name': meta.install_name
        , 'description': meta.install_description, 'title': meta.install_title
           }

    return render(request, 'inc/installation.html', ctx)


# design page
def design(request):
    meta = meta_info('home')
    ctx = {
        'name': meta.design_name
        , 'description': meta.design_description, 'title': meta.design_title
    }

    return render(request, 'inc/design.html', ctx)


# wishlist
def wishlist(request, **kwargs):
    if not request.user.is_authenticated:
        return redirect('application:login')

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
            accessory = Accessories.objects.select_related('accessories_type').get(pk=kwargs['pk'])
            WishList.objects.create(user=request.user, accessories=accessory)
            return redirect('application:list_wishlist')
    else:
        my_wishlist = WishList.objects.select_related('worktop', 'kitchen', 'unit', 'appliances').filter(
            user=request.user)
        ctx = {'wishlist': my_wishlist}
        meta = meta_info('home')
        ctx['title'] = meta.wishlist_title
        ctx['name'] = meta.wishlist_name
        ctx['description'] = meta.wishlist_description
        return render(request, 'wishlist.html', ctx)


def add_review(request, **kwargs):
    if not request.user.is_authenticated:
        return redirect('application:login')

    if request.method == 'POST':

        # appliance review addition
        if request.POST['name'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            review = Review.objects.create(
                user=request.user, rating=request.POST['rating'], comment=request.POST['comment'], appliances=appliance,
                approval='Pending')
            return redirect(
                reverse_lazy('application:appliances-detail-view',
                             kwargs={'name': 'appliance', 'slug': appliance.category.slug, 'pk': appliance.pk}))

        # worktop review addition
        elif request.POST['name'] == 'worktop':
            worktop = WorkTop.objects.select_related('category').get(pk=kwargs['pk'])
            Review.objects.create(
                user=request.user, rating=request.POST['rating'], comment=request.POST['comment'], worktop=worktop,
                approval='Pending'
            )
            return redirect(
                reverse_lazy('application:worktop-detail-view',
                             kwargs={'name': 'worktop', 'slug': worktop.category.slug, 'pk': kwargs['pk']}))
        elif request.POST['name'] == 'accessories':
            accessories = Accessories.objects.select_related('accessories_type').get(pk=kwargs['pk'])
            Review.objects.create(
                user=request.user, rating=request.POST['rating'], comment=request.POST['comment'],
                accessories=accessories,
                approval='Pending'
            )
            return redirect(
                reverse_lazy('application:accessories-detail',
                             kwargs={'slug': accessories.accessories_type.slug, 'pk': accessories.pk}))


def search(request, **kwargs):
    if request.method == 'POST':
        data = request.POST['search']
        # data = json.loads(request.body)
        qs1 = WorkTop.objects.filter(Q(name__icontains=data) | Q(description__icontains=data))
        qs2 = Appliances.objects.filter(Q(name__icontains=data) | Q(description__icontains=data))
        qs3 = Accessories.objects.filter(Q(description__icontains=data))
        ctx = {'qs1': qs1, 'qs2': qs2, 'qs3': qs3}
        meta = meta_info('home')
        ctx['title'] = meta.search_title
        ctx['name'] = meta.search_name
        ctx['description'] = meta.search_description
        return render(request, 'search.html', ctx)


class BlogList(generic.ListView):
    model = Blogs
    template_name = 'blog.html'
    context_object_name = 'list'

    def get_context_data(self, **kwargs):
        ctx = super(BlogList, self).get_context_data(**kwargs)
        meta = meta_info('home')
        ctx['name'] = meta.blog_name
        ctx['title'] = meta.blog_title
        ctx['description'] = meta.blog_description
        return ctx


class BlogDetail(generic.DetailView):
    model = Blogs
    template_name = 'blog_detail.html'
    context_object_name = 'detail'


def newsletter_subscribe(request):
    print(request.body)
    data = json.loads(request.body)
    print(data)
    already_exist = Newsletter.objects.filter(email=data['email'])
    if already_exist:
        return JsonResponse({'added': 'not added'})
    Newsletter.objects.create(email=data['email'])
    email_send(data['email'], 'newsletter')


def newsletter(request):
    if request.body and not request.POST:
        newsletter_subscribe(request)
        return JsonResponse({'added': 'added'})
    if request.method == 'GET':
        return render(request,'subscribe.html')
    if request.POST:
        already_exist = Newsletter.objects.filter(email=request.POST['email'])
        if already_exist:
            messages.warning(request,'You have already subscribed')
            return redirect('application:newsletter')
        Newsletter.objects.create(email=request.POST['email'])
        email_send(request.POST['email'], 'newsletter')
        messages.success(request, 'You have now subscribed')
        return redirect('application:newsletter')

def terms(request):
    worktop = Worktop_category.objects.all()
    ctx = {}
    meta = meta_info('home')
    ctx['name'] = meta.terms_name
    ctx['title'] = meta.terms_title
    ctx['description'] = meta.terms_description
    return render(request, 'TERMS OF SERVICE 5 (40).html', ctx)


def disclaimer(request):
    ctx = {}
    meta = meta_info('home')
    ctx['name'] = meta.disclaimer_name
    ctx['title'] = meta.disclaimer_title
    ctx['description'] = meta.disclaimer_description
    return render(request, 'Disclaimer1 (37).html', ctx)


def cancel(request):
    ctx = {}
    meta = meta_info('home')
    ctx['name'] = meta.cancellation_name
    ctx['title'] = meta.cancellation_title
    ctx['description'] = meta.cancellation_description
    return render(request, 'CANCELLATION POLICY (16).html', ctx)


def intellectual(request):
    ctx = {}

    meta = meta_info('home')
    ctx['name'] = meta.ip_name
    ctx['title'] = meta.ip_title
    ctx['description'] = meta.ip_description
    return render(request, 'Intellectual Property Notification (8).html', ctx)


def Gdp(request):
    ctx = {}
    meta = meta_info('home')
    ctx['name'] = meta.gdpr_name
    ctx['title'] = meta.gdpr_title
    ctx['description'] = meta.gdpr_description
    return render(request, 'GDPR Privacy Policy2 (44).html', ctx)


def FAQ(request):
    ctx = {}
    meta = meta_info('home')
    ctx['name'] = meta.faq_name
    ctx['title'] = meta.faq_title
    ctx['description'] = meta.faq_description
    return render(request, 'FAQ.html', ctx)


def Return(request):
    ctx = {}
    meta = meta_info('home')
    ctx['name'] = meta.return_name
    ctx['title'] = meta.return_title
    ctx['description'] = meta.return_description
    return render(request, 'Return and Refund Policy (2) (6).html', ctx)


def ship(request):
    ctx = {}
    meta = meta_info('home')
    ctx['name'] = meta.shipping_name
    ctx['title'] = meta.shipping_title
    ctx['description'] = meta.shipping_description
    return render(request, 'Shipping and Delivery Policy 1 (22).html', ctx)


def cook(request):
    ctx = {}
    meta = meta_info('home')
    ctx['name'] = meta.cookies_name
    ctx['title'] = meta.cookies_title
    ctx['description'] = meta.cookies_description
    return render(request, 'Cookies Policy3 (42).html', ctx)


def install_contact(request):
    if request.method == 'POST':
        details = f"{request.POST['detail']} from the {request.META.get('HTTP_REFERER')} /{datetime.now()}"
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
        html_content = render_to_string('inc/my_install_email.html', {'detail': contact_instance})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            'Installation Service',
            text_content,
            None,
            ['service@tkckitchens.co.uk', 'kashif@tkckitchens.co.uk']
        )
        email.attach_alternative(html_content, 'text/html')
        email.send()
        messages.info(request,
                      'Your form has been submitted. One of our customer care representative will contact you soon!')
        return redirect(request.META.get('HTTP_REFERER'))
    meta = meta_info('home')
    ctx = {'name': meta.install_form_name, 'title': meta.install_form_title,
           'description': meta.install_form_description}
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
    ctx = {'form': form}
    myuser = User.objects.get(username=request.user)
    ctx['email'] = myuser.email
    return render(request, 'checkout.html', ctx)


def temp_checkout(request, **kwargs):
    info = UserInfo.objects.get(pk=request.session.get('user_info_pk'))
    my_cart = Cart.objects.select_related('user').filter(user=request.user, checkedout=False)
    kitchen_ids = my_cart.values('kitchen_order__kitchen_id')

    complete_order = CompleteOrder.objects.create(user=info)
    complete_order.order.add(*my_cart)
    Cart.objects.filter(user=request.user, checkedout=False).update(checkedout=True)
    for id in kitchen_ids:
        Combining.objects.select_related('user', 'kitchen').filter(user=request.user, kitchen=Kitchen.objects.get(
            id=id['kitchen_order__kitchen_id'])).update(checkout=True)

    email_send(info.email_address, 'order')
    html_content = render_to_string('inc/order_detail_email.html', {'detail': complete_order})
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        'Order Created',
        text_content,
        None,
        ['service@tkckitchens.co.uk', 'kashif@tkckitchens.co.uk']
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()
    return render(request, 'temp_checkout.html')


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


def google_verification(request):
    return render(request, 'google.html')
