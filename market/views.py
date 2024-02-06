from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from .models import Pair
# Create your views here.

class Dash(TemplateView):
    template_name = 'market/home.html'

class Portfolio(TemplateView):
    template_name = 'market/portfolio.html'

class Market(TemplateView):
    template_name = 'market/market.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pairs'] = Pair.objects.all()
        return context

class PairList(TemplateView):
    template_name = 'market/pairlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pair'] = Pair.objects.get(pk=kwargs['pair_pk'])
        #context['buy_orders'] = Order.objects.filter(Q(type=1))
        return context

