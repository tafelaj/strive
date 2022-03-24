from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views.generic import TemplateView, FormView, CreateView
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.db.models import Q
from . import forms
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .models import Account, Deposit, Withdraw
from loans.models import LoanAccount

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
        #get loans
        try:
            loans = LoanAccount.objects.get(user=request.user).get_loan_total()
        except LoanAccount.DoesNotExist:
            loans = 0

        # get user savings
        try:
            savings = Account.objects.get(user=request.user, account_type='1').get_savings_total()
        except Account.DoesNotExist:
            savings = 0
        context = {'assets': assets, 'loans': loans, 'savings': savings}
        return render(request, self.template_name, context)

class SavingsView(FormView):
    template_name = 'investor/savings.html'

    def get(self, request, *args, **kwargs):
        available_balance = 12
        # get user savings
        try:
            savings = Account.objects.get(Q(user=request.user) & Q(account_type='1'))
        except Account.DoesNotExist:
            savings = None

        # get available-balance
        #todo available_balance =

        # get all deposits
        deposits = Deposit.objects.filter(Q(user=request.user) & Q(spent=False))

        #get interest earned

        #get total balance
        #todo all unspent deposits + interest earned

        # get cumulative balance
        cumulative_balance = 0
        for deposit in deposits:
            cumulative_balance += deposit.amount

        context = {'savings': savings, 'available_balance': available_balance, 'cumulative_balance': cumulative_balance,
                   'deposits': deposits,}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        amount = float(request.POST.get('deposit_amount'))
        #check if we already have an account
        try:
            account = Account.objects.get(user=request.user, account_type='1')
        except Account.DoesNotExist:
            account = Account.objects.create(user=request.user)
        except Account.MultipleObjectsReturned:
            messages.error(request, 'Something Went Wrong: error 4**')
            return HttpResponseRedirect('investor:savings')
        try:
            Deposit.objects.create(user=request.user, amount=amount, account=account)
            messages.success(request, 'Deposit request received, Please Await Confirmation')
            #todo add and info icon on all pending deposits
        except:
            #todo figure out what errors can result
            messages.error(request, 'We Could Not Process Your Deposit Request')
        return HttpResponseRedirect(reverse_lazy('investor:savings'))

class SavingsWithdraw(FormView):
    def post(self, request, *args, **kwargs):
        # create a withdraw request
        amount = float(request.POST.get('withdraw_amount'))
        available_balance = float(request.POST.get('available_balance'))
        if amount <= available_balance:
            # created withdraw request
            try:
                Withdraw.objects.create(user=request.user, amount=amount)
                messages.success(request, 'Your Withdraw request has been submitted and is awaiting approval')
            except:
                messages.error(request, 'Something Went Horribly wrong ;-)')
        else:
            messages.error(request, 'You asked to withdraw more money than you have in your available balance, we can\'t do that.')
            return HttpResponseRedirect(reverse_lazy('investor:savings'))
        return HttpResponseRedirect(reverse_lazy('investor:savings'))

