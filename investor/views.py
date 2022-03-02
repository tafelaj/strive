from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views.generic import TemplateView, FormView, CreateView
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from . import forms
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

# Create your views here.
class Landing(TemplateView):
    template_name = 'investor/landing.html'

class ComingSoon(TemplateView):
    template_name = 'investor/coming_soon.html'

class Login(FormView):
    template_name = 'registration/login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse_lazy('investor:home'))
        else:
            error = 'Your Account Was Not Found. Check Your Username and Password. ' \
                    'Contact Your Admin If The Problem Persists.'
            context = {
                'error': error
            }
            return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return render(request, self.template_name)
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('investor:home'))


class SignUpView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = forms.SignUpForm
    template_name = 'registration/signup_form.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.nrc
        user.save()
        login(self.request, user)
        return redirect('investor:home')

    def form_invalid(self, form):
        messages.error(self.request, 'The Form Did Not Validate')
        return redirect('investor:user_create')


class Home(TemplateView):
    template_name = 'investor/dash.html'

    def get(self, request, *args, **kwargs):
        assets = 0
        loans = 0
        savings = 0
        context = {'assets': assets, 'loans': loans, 'savings': savings}
        return render(request, self.template_name, context)