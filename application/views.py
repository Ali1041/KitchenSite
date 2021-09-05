import json
from datetime import datetime

from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as log
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.serializers import serialize
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views import generic

from .filters import *
from .forms import *
from .utils import get_captcha, random_queryset, display_error_messages, meta_static

# Create your views here.
User = get_user_model()
register = template.Library()


# sign up view
def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.set_password(request.POST['password'])
            form.save()
        else:
            err_msgs = display_error_messages(form)
            messages.warning(request, *err_msgs)
            return redirect('application:signup')

        # email_send(user.email, 'register')
        messages.success(request, "You've registered successfully. Please Login to view prices & latest offers.")
        return redirect('application:login')
    ctx = {'form': UserRegistrationForm()}
    meta_static('signup',ctx)

    return render(request, 'signup.html', ctx)


# login view
def login(request):
    if request.method == 'POST':
        try:
            get_username = User.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            messages.warning(request, 'Invalid email or password')
            return redirect('application:login')
        user = authenticate(request, username=get_username.username, password=request.POST['password'])
        if user is not None:
            log(request, user)
            return redirect(request.session['redirect'])
        else:
            messages.warning(request, 'Enter a valid username or password!!')
            return redirect('application:login')

    ctx = {}
    meta_static('login',ctx)

    redirect_to = request.META.get('HTTP_REFERER')
    request.session['redirect'] = redirect_to
    return render(request, 'registration/login.html', ctx)


# home page
def index(request):
    if request.method == 'POST':
        if not get_captcha(request):
            messages.warning(request, 'Captcha is not valid')
            return redirect('application:index')

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
            [request.POST['email']]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send()
        messages.success(request, 'Your brochure has been sent successfully!!')
        return redirect('application:index')

    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')

    ctx = {'blog': Blogs.objects.all()[:3],
           'vapid_key': vapid_key, 'user': request.user,
           'recaptcha_key': settings.RECAPTCHA_PUBLIC_KEY}
    meta_static('home', ctx)
    return render(request, 'base.html', ctx)


# accessories list

class AccessoriesList(generic.ListView):
    model = Accessories
    template_name = 'accessories_list.html'
    context_object_name = 'list'
    paginate_by = 10

    def get_queryset(self):
        qs = Accessories.objects.select_related('accessories_type').filter(
            accessories_type__slug__iexact=self.kwargs['slug'])

        if len(self.request.GET) > 1:
            filter_result = AccessoriesFilter(self.request.GET, queryset=qs)
            qs = filter_result.qs
        return qs


# accessories detail
class AccessoriesDetail(generic.DetailView):
    model = Accessories
    template_name = 'accessories_detail.html'
    context_object_name = 'detail'

    # Adding the context
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


# ajax kitchen request

def get_kitchen(request, **kwargs):
    # Getting total kitchens
    kitchens = Kitchen.objects.select_related('kitchen_type').all()
    total_kitchens = kitchens.values('kitchen_type__name').annotate(count=Count('kitchen_type')).order_by()
    ctx = {'list': []}

    # Getting total number of instances of a particular kitchen
    for item in total_kitchens:
        color_list = []
        img_list = []
        number_of_kitchen_instances = Kitchen.objects.select_related('kitchen_type').filter(
            kitchen_type__name=item['kitchen_type__name'],
            available=True)
        inner_dict = {'name': item['kitchen_type__name'], 'description': number_of_kitchen_instances[0].description}

        # Getting all images and colors of a particular kitchen
        for i in number_of_kitchen_instances:
            color_list.append(i.color)
            img_color = Kitchen.objects.select_related('kitchen_type').filter(
                kitchen_type__name=item['kitchen_type__name'], color=i.color, available=True)
            img_list.append(img_color[0].img)

        inner_dict['colors'] = color_list
        inner_dict['imgs'] = img_list
        ctx['list'].append(inner_dict)

    meta_static('kitchen',ctx)

    return render(request, 'all_kitchen.html', ctx)


# todo: targeted optimization
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
        qs = WorkTop.objects.select_related('category').filter(category__slug__exact=self.kwargs['slug'],
                                                               available=True)
        if len(self.request.GET) != 0:
            filters = WorktopFilters(self.request.GET, queryset=qs)
            qs = filters.qs

        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super(WorktopListView, self).get_context_data(*args, **kwargs)
        if self.get_queryset():
            # to get names of all related worktops for filtering
            category_based_worktop = WorkTop.objects.select_related('category').filter(
                category=self.get_queryset().first().category)
            number_of_worktop_in_category = category_based_worktop.values('name').annotate(
                count=Count('name')).order_by()
            select_list = []
            for item in number_of_worktop_in_category:
                select_list.append(item['name'])
            ctx['select'] = select_list
        else:
            # catering the need for a custom worktop
            ctx['stone'] = 'stone'
            ctx['meta'] = Worktop_category.objects.get(worktop_type='Stone Worktops')

        ctx['product'] = 'worktop'
        return ctx


# worktop and appliance detail
class WorktopDetailView(generic.DetailView):
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
        qs = []
        if self.kwargs['name'] == 'worktop':
            qs = WorkTop.objects.select_related('category').filter(pk=self.kwargs['pk'])
        elif self.kwargs['name'] == 'appliance':
            qs = Appliances.objects.select_related('category').filter(pk=self.kwargs['pk'])
        return qs


class AppliancesListView(generic.ListView):
    model = Appliances
    template_name = 'worktop.html'
    context_object_name = 'list'
    paginate_by = 10

    def get_queryset(self):
        qs = Appliances.objects.select_related('category').filter(category__slug__exact=self.kwargs['slug'],
                                                                  available=True)
        filters = AppliancesFilters(self.request.GET, queryset=qs)
        if len(self.request.GET) != 0:
            qs = filters.qs
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super(AppliancesListView, self).get_context_data(*args, **kwargs)
        if self.get_queryset():
            # getting appliances names in select_list for filtering
            category_based_appliances = Appliances.objects.select_related('category').filter(
                category=self.get_queryset().first().category)
            num_of_appliances_in_category = category_based_appliances.values('appliance_category').annotate(
                count=Count('appliance_category')).order_by()
            select_list = []
            for item in num_of_appliances_in_category:
                select_list.append(item['appliance_category'])
            ctx['select'] = select_list
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

    for item in cart:

        # Price calculation for worktops
        if item.worktop:
            if item.sample_worktop == 'Yes':
                sample_price += 5
            else:
                price += item.worktop.price * item.qty
            worktop_cart.append(item)

        # Price calculations for appliances
        if item.appliances:
            price += item.appliances.price * item.qty
            appliances_cart.append(item)

        #  Price calculation for accessories
        if item.accessories:
            VAT = (item.accessories.price * 20) / 100
            included_VAT = VAT + item.accessories.price
            price += included_VAT * item.qty
            accessories_cart.append(item)

        # Price calculation for kitchens and units
        if item.kitchen_order:
            if item.kitchen_order.units_intermediate_set.all():
                for i in item.kitchen_order.units_intermediate_set.all():
                    VAT = (i.unit.price * 20) / 100
                    included_VAT = VAT + i.unit.price
                    price += included_VAT * i.qty
            else:
                sample_price += 4.99

    if price < 300 and price != 0:
        price += 30

    ctx = {'cart': cart, 'accessories_cart': accessories_cart, 'worktop_cart': worktop_cart,
           'appliances_cart': appliances_cart,
           'total': price, 'feature1': random_queryset()[0],
           'feature2': random_queryset()[1]}

    return render(request, 'cart.html', ctx)


# contact form page
def contact(request):
    if request.method == 'POST':
        if not get_captcha(request):
            messages.warning(request, 'Captcha is not valid')
            return redirect('application:index')
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
            'service@tkckitchens.co.uk',
            ['service@tkckitchens.co.uk', 'kashif@tkckitchens.co.uk', 'hiphop.ali1041@gmail.com']
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=False)
        return redirect('application:contact')
    ctx = {
        'recaptcha_key': settings.RECAPTCHA_PUBLIC_KEY
    }
    meta_static('contact', ctx)

    return render(request, 'contact_us.html', ctx)


# installation page
def installation(request):
    ctx = {}
    meta_static('installation', ctx)
    return render(request, 'inc/installation.html', ctx)


# design page
def design(request):
    ctx = {}
    meta_static('design', ctx)

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
        meta_static('wishlist', ctx)

        return render(request, 'wishlist.html', ctx)


def add_review(request, **kwargs):
    if not request.user.is_authenticated:
        return redirect('application:login')

    if request.method == 'POST':

        # appliance review addition
        if request.POST['name'] == 'appliance':
            appliance = Appliances.objects.select_related('category').get(pk=kwargs['pk'])
            Review.objects.create(
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
        meta_static('search', ctx)

        return render(request, 'search.html', ctx)


class BlogList(generic.ListView):
    model = Blogs
    template_name = 'blog.html'
    context_object_name = 'list'

    def get_context_data(self, **kwargs):
        ctx = super(BlogList, self).get_context_data(**kwargs)
        meta_static('blog', ctx)

        return ctx


class BlogDetail(generic.DetailView):
    model = Blogs
    template_name = 'blog_detail.html'
    context_object_name = 'detail'


def newsletter_subscribe(request):
    data = json.loads(request.body)
    already_exist = Newsletter.objects.filter(email=data['email'])
    if already_exist:
        return JsonResponse({'added': 'not added'})
    Newsletter.objects.create(email=data['email'])
    email_send(data['email'], 'newsletter')


def newsletter(request):
    if request.body:
        data = json.loads(request.body)
        already_exist = Newsletter.objects.filter(email=data['email'])
        if already_exist:
            return JsonResponse({'added': 'not added'})
        Newsletter.objects.create(email=data['email'])
        email_send(data['email'], 'newsletter')


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
    ctx = {}
    meta_static('installation', ctx)

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
        if not get_captcha(request):
            messages.warning(request, 'Captcha is not valid')
            return redirect('application:checkout')

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
                postcode=data['postcode'],
                country=data['country'],
            )
            request.session['user_info_pk'] = info.pk
            return redirect('application:create-order')
    ctx = {'form': form, 'recaptcha_key': settings.RECAPTCHA_PUBLIC_KEY}
    myuser = User.objects.get(username=request.user)
    ctx['email'] = myuser.email
    return render(request, 'checkout.html', ctx)


def temp_checkout(request, **kwargs):
    info = UserInfo.objects.get(pk=request.session.get('user_info_pk'))
    my_cart = Cart.objects.select_related('user').filter(user=request.user, checkedout=False)
    kitchen_ids = my_cart.values('kitchen_order__kitchen_id')
    for id in kitchen_ids:
        if id['kitchen_order__kitchen_id'] != None:
            Combining.objects.select_related('user', 'kitchen').filter(user=request.user, kitchen=Kitchen.objects.get(
                id=id['kitchen_order__kitchen_id'])).update(checkout=True)

    complete_order = CompleteOrder.objects.create(user=info)
    complete_order.order.add(*my_cart)
    Cart.objects.filter(user=request.user, checkedout=False).update(checkedout=True)
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


def google_verification(request):
    return render(request, 'google.html')


# custom error handling pages
# 403 error page
def error_403(request, exception):
    return render(request, '403.html')


# 404 error page
def error_404(request, exception):
    # if 'adminPanel' in request.META.get('HTTP_REFERER',None):
    #     error_403(request, exception)

    return render(request, '403.html')


# 500 error page
def error_500(request):
    return render(request, '404.html')


# todo: async tasks of sending emails pending


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


# Static pages
def terms(request):
    ctx = {}
    meta_static('terms', ctx)
    return render(request, 'TERMS OF SERVICE 5 (40).html', ctx)


def disclaimer(request):
    ctx = {}
    meta_static('disclaimer', ctx)

    return render(request, 'Disclaimer1 (37).html', ctx)


def cancel(request):
    ctx = {}
    meta_static('cancel', ctx)

    return render(request, 'CANCELLATION POLICY (16).html', ctx)


def intellectual(request):
    ctx = {}

    meta_static('ip', ctx)

    return render(request, 'Intellectual Property Notification (8).html', ctx)


def Gdp(request):
    ctx = {}
    meta_static('gdp', ctx)

    return render(request, 'GDPR Privacy Policy2 (44).html', ctx)


def FAQ(request):
    ctx = {}
    meta_static('faq', ctx)

    return render(request, 'FAQ.html', ctx)


def Return(request):
    ctx = {}
    meta_static('return', ctx)

    return render(request, 'Return and Refund Policy (2) (6).html', ctx)


def ship(request):
    ctx = {}
    meta_static('shipment', ctx)

    return render(request, 'Shipping and Delivery Policy 1 (22).html', ctx)


def cook(request):
    ctx = {}
    meta_static('cookie', ctx)

    return render(request, 'Cookies Policy3 (42).html', ctx)

# counting of cart items
def cart_count(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {'Count': Cart.objects.select_related('user').filter(user=request.user, checkedout=False).count()})
    else:
        return JsonResponse({'Count': 0})