from django.shortcuts import render, HttpResponseRedirect, redirect
from django.views.generic import TemplateView, ListView, FormView, DetailView
from loans_admin.models import Loan, LoanPayment, Customer, Expenses, Summery
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
        loans = Loan.objects.filter(Q(station=request.user.station) & Q(status='1') | Q(status='2'))

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

 # payments...
class PaymentsView(ListView):
    template_name = 'loans_admin/payments.html'
    model = LoanPayment
    context_object_name = 'payments'
    paginate_by = '30'

    def get_queryset(self):
        payments = LoanPayment.objects.filter(Q(station=self.request.user.station)).order_by('-id')
        return payments

# payments end ....


class CustomerView(ListView):
    template_name = 'loans_admin/customers.html'
    model = Customer
    context_object_name = 'customers'
    paginate_by = '30'

    def get_queryset(self):
        q = Customer.objects.filter(station=self.request.user.station).order_by('-id')
        return q


class PendingLoansView(FormView):
    template_name = 'loans_admin/pending_loan_list.html'

    def get(self, request, *args, **kwargs):
        loans = Loan.objects.filter(Q(station=request.user.station) & Q(status='1')).order_by('-id')

        context = {'loans': loans, }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        approved_amount = request.POST.get('approved_amount')
        loan_id = request.POST.get('loan_id')
        try:
            loan = Loan.objects.get(pk=loan_id)
            if loan.amount == approved_amount:
                loan.status = '2'
                loan.save()
            else:
                loan.amount = approved_amount
                loan.status = '2'
                loan.save()

        except Loan.DoesNotExist:
            messages.error(request, 'I couldn\'t The Loan For Some Reason. I must be drunk')
            return HttpResponseRedirect(reverse_lazy('loans_admin:pending_loans'))
        messages.success(request, 'Loan Approved')
        return HttpResponseRedirect(reverse_lazy('loans_admin:active_loans'))


class LoansView(FormView):
    template_name = 'loans_admin/loan_list.html'

    def get(self, request, *args, **kwargs):
        loans = Loan.objects.filter(Q(station=request.user.station) & Q(status='2'))

        context = {'loans': loans,}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #record payment
        amount = request.POST.get('amount')
        loan_id = request.POST.get('loan_id')
        payment_type = request.POST.get('payment_type')
        try:
            loan = Loan.objects.get(pk=loan_id)
            payment = LoanPayment.objects.create(loan=loan, received_by=request.user, amount=amount,
                                                 station=request.user.station, payment_type=payment_type)
            payment.balance = loan.get_balance()
            payment.save()
            if loan.get_balance() == 0:
                loan.status = '3'
                loan.save()
                messages.info(request, 'Loan Has Been Paid In full')
        except Loan.DoesNotExist:
            messages.error(request, 'I couldn\'t The Loan For Some Reason. I must be drunk')
            return HttpResponseRedirect(reverse_lazy('loans_admin:active_loans'))
        messages.success(request, 'Payment Of K{} For Loan ID {} Recorded Successfully'.format(amount, loan.get_loan_id()))
        return redirect('loans_admin:loan_details', pk=loan.id)


class LoanDetails(DetailView):
    template_name = 'loans_admin/loan_details.html'
    model = Loan
    context_object_name = 'loan'

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
        day = datetime.today().day
        month = datetime.today().month
        year = datetime.today().year
        # opening balance
        try:
            opening_balance = Summery.objects.get(Q(station=request.user.station) & Q(date__day=day) &
                                                  Q(date__month=month) & Q(date__year=year))
        except Summery.DoesNotExist:
            opening_balance = None

        # payments
        today_payments = LoanPayment.objects.filter(Q(date__day=day) & Q(date__month=month) & Q(date__year=year) &
                                                    Q(station=self.request.user.station)).order_by('-id')
        payments_total = 0
        for payment in today_payments:
            payments_total += payment.amount

        # loans today
        loans = Loan.objects.filter(Q(station=request.user.station) &
                                    Q(issue_date__day=day) & Q(issue_date__month=month) &
                                    Q(issue_date__year=year))

        approved_loans = loans.filter(status='2')
        approved_loans_total = 0
        for loan in approved_loans:
            approved_loans_total +=loan.amount

        pending_loans = loans.filter(status='1')
        pending_loans_total = 0
        for loan in pending_loans:
            pending_loans_total +=loan.amount

        # Expenses
        expenses = Expenses.objects.filter(Q(station=request.user.station) & Q(date__day=day) & Q(date__month=month)
                                           & Q(date__year=year))
        expenses_total = 0
        for expense in expenses:
            expenses_total += expense.amount

        #expected_cash
        # expected_cash = opening_bal + payments_total - issued_loans - expenses
        try:
            expected_cash = opening_balance.balance_brought_forward + payments_total - approved_loans_total - expenses_total
        except AttributeError:
            expected_cash = 0 + payments_total - approved_loans_total - expenses_total
        context = {'expected_cash': expected_cash,'today_payments':today_payments, 'loans': loans,
                   'approved_loans_total': approved_loans_total,
                   'pending_loans_total': pending_loans_total, 'expenses': expenses, 'expenses_total': expenses_total,
                   'payments_total': payments_total, 'opening_balance': opening_balance}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if request.POST.get('expense'):
            expense = Expenses.objects.create(amount=request.POST.get('amount'),
                                              description=request.POST.get('description'), user=request.user,
                                              station=request.user.station)
            messages.success(request, 'Expense For K {} Recorded.'.format(expense.amount))
            return HttpResponseRedirect(reverse_lazy('loans_admin:summary'))
        else:
            day = datetime.today().day
            month = datetime.today().month
            year = datetime.today().year

            #get summery
            try:
                summery = Summery.objects.get(Q(station=request.user.station) & Q(date__day=day) &
                                                  Q(date__month=month) & Q(date__year=year))
            except Summery.DoesNotExist:
                messages.error(request, 'I must be drunk or something because i couldn\'t find the summary for today')
                return HttpResponseRedirect(reverse_lazy('loans_admin:summary'))
            # calculate profits for the day
            # get all payments from today
            today_profits = 0
            payments = LoanPayment.objects.filter(Q(station=request.user.station) & Q(date__day=day) &
                                                  Q(date__month=month) & Q(date__year=year))
            for payment in payments:
                today_profits += payment.get_profits()

            #fill it in
            summery.total_profits = today_profits
            summery.total_payments = float(request.POST.get('total_payments'))
            summery.total_expenditure = float(request.POST.get('total_expenditure'))
            summery.total_pending_loans = float(request.POST.get('total_pending_loans'))
            summery.total_active_loans = float(request.POST.get('approved_loans_total'))
            summery.total_expected_cash = float(request.POST.get('total_expected_cash'))
            summery.total_cash_at_hand = float(request.POST.get('cash_at_hand'))
            summery.closed = True
            summery.save()
            messages.success(request, 'Business Closed For Today')
            return HttpResponseRedirect(reverse_lazy('loans_admin:summary'))


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

        messages.success(request, 'Loan Application Recorded')
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
        messages.success(request, 'Loan Application Recorded')
        return HttpResponseRedirect(reverse_lazy('loans_admin:pending_loans'))

class LoanRejection(FormView):
    def post(self, request, *args, **kwargs):
        loan_id = request.POST.get('loan_id')
        try:
            loan = Loan.objects.get(pk=loan_id)
            loan.status = '4'
            loan.save()
            messages.success(request, 'loan Rejected')
        except Loan.DoesNotExist:
            messages.error(request, 'I could not reject the loan because someone has already thrown it away')
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

# opening balance
class SaveOpeningBalance(FormView):
    def post(self, request, *args, **kwargs):
        opening_bal = request.POST.get('opening_bal')
        summary = Summery.objects.create(station=request.user.station, user=request.user)
        summary.balance_brought_forward = opening_bal
        summary.save()
        return HttpResponseRedirect(reverse_lazy('loans_admin:summary'))