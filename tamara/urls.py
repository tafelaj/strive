from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'tamara'

urlpatterns = [
    path('', views.Landing.as_view(), name="tamara_landing"),
    path('dash/', views.Dashboard.as_view(), name='tamara_dash'),
    path('car/list/', views.CarList.as_view(), name='car_list'),
    path('car/<int:pk>/details/', views.CarDetails.as_view(), name='car_details'),
]