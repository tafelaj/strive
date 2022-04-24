from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, ListView, FormView
from loans_admin.models import Loan, LoanPayment, Customer
from investor.models import Station
from django.db.models import Q
from datetime import datetime
from loans_admin import forms
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.


class Dash(TemplateView):
    template_name = 'loans_admin/dash.html'

    def get(self, request, *args, **kwargs):
        #available capital
        available_cap = 0
        #get loans
        loans_total = 0

        #number of stations
        stations = Station.objects.filter(institution=request.user.station.institution).count()

        loans_and_profit = 0
        loans = Loan.objects.filter(Q(station=request.user.station))

        # active_loans
        active_loans = loans.filter(status='2')

        # pending loans
        pending_loans = loans.filter(status='1')
        pending_loans_total = 0
        for loan in pending_loans:
            pending_loans_total += loan.amount

        for loan in active_loans:
            loans_total += loan.amount
            loans_and_profit += loan.get_total_amount()

        #total interest
        total_interest = loans_and_profit - loans_total
        context = {'loans': loans, 'active_loans': active_loans, 'pending_loans': pending_loans, 'pending_loans_total': pending_loans_total, 'loans_total': loans_total, 'total_interest': total_interest, 'available_cap': available_cap,
                   'loans_and_profit': loans_and_profit, 'stations': stations,}
        return render(request, self.template_name, context)

class PaymentsView(ListView):
    template_name = 'loans_admin/payments.html'
    model = LoanPayment
    context_object_name = 'payments'

    def get_queryset(self):
        day = datetime.today().day
        month = datetime.today().month
        year = datetime.today().year
        today_payments = LoanPayment.objects.filter(Q(date__day=day) & Q(date__month=month) & Q(date__year=year) & Q(station=self.request.user.station))
        return today_payments

class CustomerView(ListView):
    template_name = 'loans_admin/customers.html'
    model = Customer
    context_object_name = 'customers'

    def get_queryset(self):
        q = Customer.objects.filter(station=self.request.user.station)
        return q


class PendingLoansView(FormView):
    template_name = 'loans_admin/pending_loan_list.html'

    def get(self, request, *args, **kwargs):
        loans = Loan.objects.filter(Q(station=request.user.station) & Q(status='1'))

        context = {'loans': loans, }
        return render(request, self.template_name, context)


class LoansView(FormView):
    template_name = 'loans_admin/loan_list.html'

    def get(self, request, *args, **kwargs):
        loans = Loan.objects.filter(Q(station=request.user.station) & Q(status='2'))

        context = {'loans': loans,}
        return render(request, self.template_name, context)


class CompletedLoans(ListView):
    template_name = 'loans_admin/paid_loans.html'
    model = Loan
    context_object_name = 'loans'

    def get_queryset(self):
        q = Loan.objects.filter(Q(station=self.request.user.station) & Q(status='3'))
        return q

class SummaryView(FormView):
    template_name = 'loans_admin/summary.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)

class IssueLoanNewCustomer(FormView):
    template_name = 'loans_admin/issue_loan.html'

    def get(self, request, *args, **kwargs):
        #new customer form
        customer_form = forms.CustomerForm()
        # new loan form
        loan_form = forms.LoanForm()

        context={'customer_form': customer_form, 'loan_form': loan_form,}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #save new customer
        customer_form = forms.CustomerForm(request.POST or None)
        if customer_form.is_valid():
            customer = customer_form.save(commit=False)
            customer.station = request.user.station
            customer.save()
        else:
            messages.error(request, 'The Customer Form Did Not Validate')
            return HttpResponseRedirect(reverse_lazy('loans_admin:new_loan_new'))

        #save new customer loan
        loan_form = forms.LoanForm(request.POST or None)
        if loan_form.is_valid():
            loan = loan_form.save(commit=False)
            loan.customer = customer
            loan.issued_by = request.user
            loan.station = request.user.station
            loan.save()
        else:
            messages.error(request, 'The Loan Form Did Not Validate')
            return HttpResponseRedirect(reverse_lazy('loans_admin:new_loan_new'))

        return HttpResponseRedirect(reverse_lazy('loans_admin:pending_loans'))


class IssueLoanExistingCustomer(FormView):
    template_name = 'loans_admin/issue_loan.html'

    def get(self, request, *args, **kwargs):
        # new loan form
        loan_form = forms.LoanForm()

        #get existing customers
        customers = Customer.objects.filter(station=request.user.station)

        context = {'loan_form': loan_form, 'customers': customers,}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #save new customer
        customer_id = request.POST.get('customer_id')
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            messages.error(request, 'Weirdly We Couldn\'t Find The Customer, Please Try Again')
            return HttpResponseRedirect(reverse_lazy('loans_admin:new_loan_existing'))

        #save new customer loan
        loan_form = forms.LoanForm(request.POST or None)
        if loan_form.is_valid():
            loan = loan_form.save(commit=False)
            loan.customer = customer
            loan.issued_by = request.user
            loan.station = request.user.station
            loan.save()
        else:
            messages.error(request, 'The Loan Form Did Not Validate')
            return HttpResponseRedirect(reverse_lazy('loans_admin:new_loan_existing'))

        return HttpResponseRedirect(reverse_lazy('loans_admin:pending_loans'))


#legal
class TermsView(TemplateView):
    template_name = 'loans_admin/t_and_c.html'


#stations
class StationsView(FormView):
    #implementation formset for all user stations if user is admin
    template_name = 'loans_admin/stations.html'
    def get(self, request, *args, **kwargs):
        stations_for_institution = Station.objects.filter(institution=request.user.station.institution)
        formset = forms.StationInventoryFormSet(queryset=stations_for_institution)

        context = {'formset': formset,}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        stations_for_institution = Station.objects.filter(institution=request.user.station.institution)
        formset = forms.StationInventoryFormSet(request.POST or None, queryset=stations_for_institution)
        if formset.is_valid():
            with transaction.atomic():
                instances = formset.save(commit=False)

                for instance in instances:
                    instance.institution = request.user.station.institution
                    instance.save()
                messages.success(request, 'Stations Updated Successfully')
        else:
            messages.error(request, 'The Formset Did Not Validate, But don\'t ask me why; i don\'t know')
        return HttpResponseRedirect(reverse_lazy('loans_admin:loans_admin_home'))