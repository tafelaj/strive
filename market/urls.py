from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'market'

urlpatterns = [
    path('', views.Dash.as_view(), name="market_dash"),
    path('market/', views.Market.as_view(), name="market"),
    path('market/pair/<int:pair_pk>/order/list', views.PairList.as_view(), name="pair_list"),
    path('portfolio/', views.Portfolio.as_view(), name="Portfolio"),
    path('help/', views.Dash.as_view(), name="help"),
    ]