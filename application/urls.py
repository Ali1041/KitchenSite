from django.urls import path, include
from .views import *
from django.contrib.auth.views import LogoutView


app_name = 'application'

urlpatterns = [
    path('', index, name='index'),

    # auth urls
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # ajax call
    path('get-images/<str:name>/', img_urls, name='get-images'),

    # kitchen
    path('all-kitchen/', AllKitchenView.as_view(), name='all-kitchen'),
    path('kitchen-view/<int:pk>/', KitchenView.as_view(), name='kitchen-view'),
    path('unit-change/<int:pk>/<str:name>/<int:qty>/', unit_change, name='unit-change'),

    # worktop
    path('worktop/<int:pk>/', WorktopListView.as_view(), name='worktop-view'),
    path('wokrtop-detail/<str:name>/<int:pk>/', WorktopDetailView.as_view(), name='worktop-detail-view'),

    # appliances
    path('appliances/<int:pk>/', AppliancesListView.as_view(), name='appliances-list'),
    path('appliances-detail<str:name>/<int:pk>/', WorktopDetailView.as_view(), name='appliances-detail-view'),

    # cart
    path('add-to-cart/<str:product>/<str:name>/<int:pk>/<int:qty>/<str:process>/', addcart, name='add-to-cart'),
    path('cart/', cart, name='cart'),

    # misllaneous
    path('contact-us/', contact, name='contact'),
    path('installation/', installation, name='installation'),
    path('design/', design, name='design'),
    path('add-to-wishlist/<str:product>/<int:pk>/', wishlist, name='wishlist'),
    path('wishlist/', wishlist, name='list_wishlist'),
    path('add-review/<int:pk>/', add_review, name='review'),
    path('search/', search, name='search'),
    path('blog-list/', BlogList.as_view(), name='blog-list'),
    path('blog-detail/<int:pk>/', BlogDetail.as_view(), name='blog-detail'),
    path('terms-and-conditions/', terms, name='terms'),
    path('shipping-policy/', ship, name='shippping'),
    path('FAQ/', FAQ, name='FAQ'),
    path('return-refund/', Return, name='return-policy'),
    path('Cancellation-policy/', cancel, name='canel'),
    path('GDPR/', Gdp, name='GDPR'),
    path('Cookies/', cook, name='cookies'),
    path('intellectual-property-notification/', intellectual, name='intelectual'),
    path('disclaimer/', disclaimer, name='disclaimer'),

    # path('doors/cabnets/<int:pk>/<str:name>/', choose, name='choose'),
    path('subscribe/', newsletter, name='newsletter'),

    path('install-contact/', install_contact, name='installation_contact'),

    # checkout
    path('checkout/', checkout, name='checkout'),
    path('order-creation/', create_order_klarna, name='create-order'),
    path('order-confirmed/', confirmation, name='confirm'),
    path('push-email/',push,name='push-email'),


]
