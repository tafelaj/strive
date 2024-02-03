from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'loans'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('request/', views.RequestLoan.as_view(), name='request_loan'),
]