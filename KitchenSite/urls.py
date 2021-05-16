"""KitchenSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import \
    PasswordResetCompleteView, PasswordResetDoneView, PasswordResetView, PasswordResetConfirmView
from django.contrib.sitemaps.views import sitemap
from application.sitemaps import *
from django.views.generic import TemplateView

sitemaps = {
    'static': StaticMaps,
    'worktop': WorktopMap,
    'appliances': AppliancesMap,
    'kitchen': KitchenMap,
    'worktopDetail': WorktopsDetailMap,
    'appliancesDetail': AppliancesDetailMap,
    'accessoriesList': AccessoriesList,
    'accessoriesDetail': AccessoriesDetail,
    'blogmap': BlogsMap,
}

urlpatterns = [
                  path('admin/', admin.site.urls),

                  path('', include('application.urls')),
                  path('adminPanel/', include('adminPanel.urls')),
                  path('ckeditor', include('ckeditor_uploader.urls')),
                  re_path('djga/', include('google_analytics.urls')),
                  path('webpush/', include('webpush.urls')),
                  path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
                       name='django.contrib.sitemaps.views.sitemap'),
                  path('sw.js', TemplateView.as_view(template_name='adminPanel/sw.js', content_type='text/javascript')),
                  path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/text'),
                       name='robot'),
                  # reset password
                  path('reset_password/', PasswordResetView.as_view(template_name='registration/reset_password.html'),
                       name='reset_password'),
                  path('password_reset_done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
                  path('password_reset_confirm/<uidb64>/<token>/',
                       PasswordResetConfirmView.as_view(),
                       name='password_reset_confirm'),
                  path('password_reset_complete/',
                       PasswordResetCompleteView.as_view(template_name='registration/last_reset.html'),
                       name='password_reset_complete')

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler403 = 'application.views.error_403'
handler404 = 'application.views.error_404'
handler500 = 'application.views.error_500'
handler400 = 'application.views.error_404'
