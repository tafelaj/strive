from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'investor'

urlpatterns = [
    path('user/create/', views.SignUpView.as_view(), name='user_create'),
    path('user/login/', views.Login.as_view(), name='user_login'),
    path('', views.Home.as_view(), name='home'),
    path('savings/', views.SavingsView.as_view(), name='savings'),
    path('savings/withdraw/', views.SavingsWithdraw.as_view(), name='savings_withdraw'),
]