from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from tamara.models import Car

# Create your views here.
class Landing(TemplateView):
    template_name = 'tamara/landing.html'



class Dashboard(TemplateView):
    template_name = 'tamara/dash.html'
class CarList(ListView):
    template_name = 'tamara/car_list.html'
    model = Car
    paginate_by = 30


class CarDetails(DetailView):
    template_name = 'tamara/car_details.html'

class UserProfile(DetailView):
    pass