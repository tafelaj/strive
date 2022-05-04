from django.shortcuts import render
from django.views.generic import TemplateView
from Strive.decorators import user_is_investor
from django.utils.decorators import method_decorator

@method_decorator(user_is_investor, name='get')
class Home(TemplateView):
    template_name = 'loans/loan_home.html'
