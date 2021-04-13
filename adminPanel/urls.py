from django.urls import path
from .views import *
from django.views.generic import TemplateView

app_name = 'adminPanel'

urlpatterns = [
    path('sw.js', TemplateView.as_view(template_name='adminPanel/sw.js', content_type='application/x-javascript')),

    path('', index, name='index'),

    # kitchen urls
    path('admin-kitchen/', ListKitchenView.as_view(), name='admin-kitchen'),
    path('admin-kitchen-detail/<int:pk>/', KitchenDetailview.as_view(), name='admin-kitchen-detail'),
    path('admin-kitchen-units/<int:pk>/', UnitsList.as_view(), name='kitchen-units-detail'),
    path('admin-kitchen-add/',kitchenadd,name='admin-kitchen-add'),
    path('admin-complete-kitchen-detail/<int:pk>/',CompleteKitchenDetail.as_view(),name='complete-kitchen-detail'),
    path('admin-kitchen-units/<int:pk>',UnitsList.as_view(),name='units'),
    path('admin-kitchen-edit/<int:pk>/',addUnits,name='edit-kitchen-units'),
    path('admin-kitchen-units-add/',addUnits,name='admin-add-units'),
    # path('admin-kitchen-units-add/<int:pk>/', addUnits, name='admin-add-units'),

    path('admin-kitchen-unit-category/',addunitcategory,name='add-unit-category'),
    # path('admin-doors-cabnets-add/<str:name>/',add_doors_cabnets,name='admin_doors'),


    # worktop urls
    path('admin-worktop-category/', WorkTypeCategory.as_view(), name='admin-worktop'),
    path('admin-worktop-list/<int:pk>/', WorktopList.as_view(), name='admin-worktop-list'),
    path('admin-worktop-detail/<int:pk>/', WorktopDetail.as_view(), name='admin-worktop-detail'),
    path('admin-wokrtop-add/<str:name>/', add_worktop, name='add-worktop'),
    path('admin-wokrtop-add/<str:name>/<int:pk>/', add_worktop, name='edit-worktop'),
    path('add-worktop-category/<str:name>/',add_worktop_category,name='add-worktop-category'),

    # appliances urls
    path('admin-appliances-category/', AppliancesCategory.as_view(), name='admin-appliances'),
    path('admin-appliances-list/<int:pk>/', AppliancesList.as_view(), name='admin-appliances-list'),
    path('admin-appliances-detail/<int:pk>/', AppliancesDetail.as_view(), name='admin-appliance-detail'),

    # all orders
    path('admin-orders/', Orders.as_view(), name='admin-all-orders'),
    path('admin-order-detail/<int:pk>/', DetailOrder.as_view(), name='admin-order-detail'),

    # all users
    path('admin-orders/', all_user, name='all-users'),


    # blogs
    path('admin-blogs/',BlogsList.as_view(),name='admin-blog'),
    path('admin-add-blog/<str:to>/',create_blog,name='admin-add-blog'),
    path('admin-edit-blog/<str:to>/<int:pk>/',create_blog,name='edit-blog'),
    path('admin-detail/<int:pk>/',DetailBlog.as_view(),name='detail-blog'),

    # bulk data
    path('bulk-form/',bulk_add,name='bulk'),
    path('bulk-read/<str:name>/<str:category>/',file_reading,name='reading'),

    path('approve/',approve,name='approve'),
    path('approve/<str:name>/<int:pk>/',approving_admin,name='approved'),

    # contact us
    path('contact-list/',ContactUsList.as_view(),name='contact_list'),
    path('contact-list-detail/<int:pk>/',ContactUsDetail.as_view(),name='detail-contact'),

    # contact actual
    path('contact-us-list/',ContactActualList.as_view(),name='actual-list'),
    path('contact-us-detail/<int:pk>/',ContactActualDetail.as_view(),name='actual-detail'),


    path('all-user/',all_user,name='user'),

    path('brochure-list/',BrochureRequests.as_view(),name='brochure-list'),

    # accessories url
    path('accessories-list/',AccessoriesList.as_view(),name='accessories'),
    path('add-type-accessories/',add_accessories_type,name='accessories_type'),
    path('add-accessories/',add_accessories,name='add_accessories'),
    path('accessories-detail/<int:pk>/',AccessoriesDetail.as_view(),name='detail_accessories'),
    path('accessories-in-detail/<int:pk>/<int:pk2>/', AccessoriesInDetail.as_view(), name='detail_in_accessories'),
    path('accessories-edit/<int:pk>/',edit_accessories,name='edit-accessories'),


    # Chat options
    path('all-chat-rooms/',ChatRoomsList.as_view(),name='all_rooms'),
    # path('create-room/',create_room,name='create_room'),
    path('chat-room/<slug:slug>', room_detail, name='room'),
    # path('token/', token, name='token'),
    # path('send_push/',send_push,name='push'),

]
