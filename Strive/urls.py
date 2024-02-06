"""Strive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from investor.views import Landing, ComingSoon
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #path('', ComingSoon.as_view(), name='landing'),
    path('', Landing.as_view(), name='landing'),
    path('admin/', admin.site.urls),
    path('investor/', include('investor.urls')),
    path('loans/', include('loans.urls')),
    path('loans/admin/', include('loans_admin.urls')),
    path('market/', include('market.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)