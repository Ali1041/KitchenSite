from django.contrib.auth.views import LogoutView
from django.urls import path

from adminPanel.views import token, send_push
from .views import *

app_name = 'application'

urlpatterns = [
    path('', index, name='index'),

    # auth urls
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # accessories list
    path('kitchen-accessories/<slug:slug>/', AccessoriesList.as_view(), name='accessories-list'),
    path('kitchen-accessories/<slug:slug>/<int:pk>/', AccessoriesDetail.as_view(), name='accessories-detail'),

    # kitchen
    path('ourkitchens/', get_kitchen, name='all-kitchen'),
    path('kitchen-view/<str:name>/<str:color>/', KitchenView.as_view(), name='kitchen-view'),
    path('get-kitchens/<str:color>/', get_kitchen, name='get-kitchen'),
    path('unit-change/<int:pk>/<str:name>/<int:qty>/', unit_change, name='unit-change'),
    path('search-units/<str:search>/<str:name>/', search_units, name='search-units'),
    path('kitchen-view/unit/<str:name>/<str:color>/<int:unit>/', KitchenView.as_view(), name='unit-view'),

    # worktop
    path('worktop/<slug:slug>/', WorktopListView.as_view(), name='worktop-view'),
    path('wokrtop-detail/<str:name>/<slug:slug>/<int:pk>/', WorktopDetailView.as_view(), name='worktop-detail-view'),

    # appliances
    path('appliances/<slug:slug>/', AppliancesListView.as_view(), name='appliances-list'),
    path('appliances-detail/<str:name>/<slug:slug>/<int:pk>/', WorktopDetailView.as_view(),
         name='appliances-detail-view'),

    # cart
    path('add-to-cart/<str:product>/<str:name>/<int:pk>/<int:qty>/<str:process>/', addcart, name='add-to-cart'),
    path('cart/', cart, name='cart'),

    # misllaneous
    path('contactus/', contact, name='contact'),
    path('installationservice/', installation, name='installation'),
    path('designservice/', design, name='design'),
    path('add-to-wishlist/<str:product>/<int:pk>/', wishlist, name='wishlist'),
    path('wishlist/', wishlist, name='list_wishlist'),
    path('add-review/<int:pk>/', add_review, name='review'),
    path('searchresults/', search, name='search'),
    path('trends/', BlogList.as_view(), name='blog-list'),
    path('trends/<slug:slug>/<int:pk>/', BlogDetail.as_view(), name='blog-detail'),
    path('terms-and-conditions/', terms, name='terms'),
    path('shipping-policy/', ship, name='shippping'),
    path('FAQ/', FAQ, name='FAQ'),
    path('return-refund/', Return, name='return-policy'),
    path('Cancellation-policy/', cancel, name='canel'),
    path('GDPR/', Gdp, name='GDPR'),
    path('Cookies/', cook, name='cookies'),
    path('intellectual-property-notification/', intellectual, name='intelectual'),
    path('disclaimer/', disclaimer, name='disclaimer'),
    path('subscribe/', newsletter, name='newsletter'),
    path('HireinstallationService/', install_contact, name='installation_contact'),

    # checkout
    path('checkout/', checkout, name='checkout'),
    path('orderconfirmation/', temp_checkout, name='create-order'),
    # path('order-confirmed/', confirmation, name='confirm'),
    # path('push-email/',hello,name='push-email'),
    path('cart-count/', cart_count, name='cart-count'),

    path('google754a662932836b09.html/', google_verification, name='google-verification'),

    # Chat api integrations urls
    path('token/', token, name='token'),
    path('send_push/', send_push, name='push'),
]

