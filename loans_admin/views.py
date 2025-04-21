from django.shortcuts import render, HttpResponseRedirect, redirect
from django.views.generic import TemplateView, ListView, FormView, DetailView

import loans.forms
from loans_admin.models import Customer, Expenses, Summery
from loans.models import Loan, LoanPayment
from investor.models import Station, Deposit
from django.db.models import Q
from datetime import datetime, timedelta
from loans_admin import forms
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
#from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.


class Dash(TemplateView):
    template_name = 'loans_admin/dash.html'

    def get(self, request, *args, **kwargs):
        #available capital
        available_cap = 0
        #get loans
        loans_total = 0

        #number of stations
        #stations = Station.objects.filter(institution=request.user.station.institution).count()

        loans_and_profit = 0
        loans = Loan.objects.filter(Q(status='1') | Q(status='2'))

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
                   'loans_and_profit': loans_and_profit,}
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

class PendingPayments(ListView):
    template_name = 'loans_admin/pending_payments.html'
    model = Loan
    context_object_name = 'loans'

    def get_queryset(self):

        loans = Loan.objects.filter(Q(station=self.request.user.station) & Q(status='2'))
        all_payments = LoanPayment.objects.filter(Q(station=self.request.user.station) &
                                                  Q(date__day=datetime.today().day) &
                                                  Q(date__month=datetime.today().month) &
                                                  Q(date__year=datetime.today().year))

        for payment in all_payments:
            loans.exclude(Q(pk=payment.loan.id) & Q(issue_date__year=datetime.today().year) &
                          Q(issue_date__month=datetime.today().month) & Q(issue_date__day=datetime.today().day))
        return loans

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['pending'] = True
        return super().get_context_data(**kwargs)

# payments end ....


class CustomerView(ListView):
    template_name = 'loans_admin/customers.html'
    model = Customer
    context_object_name = 'customers'
    paginate_by = '30'

    def get_queryset(self):
        q = Customer.objects.filter(is_active=True).order_by('-id')
        return q

class UpdateCustomerView(FormView):
    template_name = 'loans_admin/update_customers.html'

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()

        formset = forms.CustomerFormSet(queryset=customers)

        context = {'formset':formset, 'show_delete': True}
        return  render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        customers = Customer.objects.all()

        formset = forms.CustomerFormSet(request.POST or None, queryset=customers)

        if formset.is_valid():
            with transaction.atomic():
                instances = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()

                for instance in instances:
                    instance.save()
                messages.success(request, 'Customers Updated Successfully')
        else:
            #print(formset.errors)
            messages.error(request, 'The Form Did Not Validate, Please Check Your Entries')
            messages.error(request, '{}'.format(formset.errors))
            return HttpResponseRedirect(reverse_lazy('loans_admin:update_customers'))
        return HttpResponseRedirect(reverse_lazy('loans_admin:customers'))


class PendingLoansView(FormView):
    template_name = 'loans_admin/pending_loan_list.html'

    def get(self, request, *args, **kwargs):
        loans = Loan.objects.filter(Q(status='1')).order_by('-id')

        context = {'loans': loans, }
        return render(request, self.template_name, context)

    #approve loans
    def post(self, request, *args, **kwargs):
        approved_amount = request.POST.get('approved_amount')
        loan_id = request.POST.get('loan_id')
        try:
            loan = Loan.objects.get(pk=loan_id)
            # set the due date
            due_date = None
            if loan.term == '1':
                due_date = datetime.today() + timedelta(7)
            elif loan.term == '2':
                due_date = datetime.today() + timedelta(14)
            elif loan.term == '3':
                due_date = datetime.today() + timedelta(30)
            elif loan == '4':
                due_date = datetime.today() + timedelta(60)
            elif loan.term =='5':
                due_date = datetime.today() + timedelta(90)

            loan.due_date = due_date
            if loan.amount != approved_amount:
                loan.amount = approved_amount

            loan.status = '2'
            loan.issue_date = timezone.now()
            loan.approved_by = request.user
            loan.save()

        except Loan.DoesNotExist:
            messages.error(request, 'I couldn\'t Find The Loan For Some Reason. I must be drunk')
            return HttpResponseRedirect(reverse_lazy('loans_admin:pending_loans'))
        messages.success(request, 'Loan Approved')
        return HttpResponseRedirect(reverse_lazy('loans_admin:active_loans'))


class LoansView(FormView):
    template_name = 'loans_admin/loan_list.html'

    def get(self, request, *args, **kwargs):
        loan_list = Loan.objects.filter(Q(status='2')).order_by('-id')

        context = {'loans': loan_list,}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # date
        date = datetime.today()

        #record payment
        amount = request.POST.get('amount')
        loan_id = request.POST.get('loan_id')
        payment_type = request.POST.get('payment_type')
        confirm_re_pay = request.POST.get('confirm_re_pay')
        print(confirm_re_pay)
        try:
            loan = Loan.objects.get(pk=loan_id)
            balance = loan.get_balance()

             # check if there is a payment for this loan for today
            existing_payments = LoanPayment.objects.filter(Q(loan=loan) & Q(date__day=date.day)& Q(date__month=date.month) & Q(date__year=date.year))

            if existing_payments.count() > 0:
                # if user knows what they are doing
                if confirm_re_pay:
                    # make the payment
                    payment = LoanPayment.objects.create(loan=loan, received_by=request.user, amount=amount,
                                                         station=request.user.station, payment_type=payment_type)
                    payment.balance = loan.get_balance()
                    payment.save()
                    if loan.get_balance() == 0:
                        loan.status = '3'
                        loan.save()
                        messages.info(request, 'Loan Has Been Paid In full')
                    messages.success(request, 'Payment Of K{} For Loan ID {} Recorded Successfully'.format(amount,
                                                                                                           loan.get_loan_id()))
                else:
                    # render template with warning
                    context = {'re_enter_message': 'A Payment For This Loan Has Already been Made Today, '
                                                    'Are you sure you want to add another?', 'amount': amount,
                                'loan_id': loan_id, 'payment_type': payment_type, 'balance': balance}
                    return render(request, self.template_name, context)

            else:
                #make the payment if none exists
                payment = LoanPayment.objects.create(loan=loan, received_by=request.user, amount=amount,
                                                 station=request.user.station, payment_type=payment_type)
                payment.balance = loan.get_balance()
                payment.save()
                if loan.get_balance() == 0:
                    loan.status = '3'
                    loan.save()
                    messages.info(request, 'Loan Has Been Paid In full')
                messages.success(request, 'Payment Of K{} For Loan ID {} Recorded Successfully'.format(amount,
                                                                                                       loan.get_loan_id()))

        except Loan.DoesNotExist:
            messages.error(request, 'I couldn\'t The Loan For Some Reason. I must be drunk')
            return HttpResponseRedirect(reverse_lazy('loans_admin:active_loans'))

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
        q = Loan.objects.filter(Q(station=self.request.user.station) & Q(status='3')).order_by('-issue_date')
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
                                    Q(issue_date__year=year)).exclude(status='3')

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


class SummaryList(ListView):
    model = Summery
    template_name = 'loans_admin/summary_list.html'
    context_object_name = 'summaries'

    def get_queryset(self):
        q = Summery.objects.filter(Q(station=self.request.user.station))
        return q

class SummeryDetail(DetailView):
    template_name = 'loans_admin/summary_details.html'
    model = Summery
    context_object_name = 'summary'

    def get_context_data(self, **kwargs):
        date = kwargs['object'].date
        kwargs['loans'] = Loan.objects.filter(Q(issue_date__day=date.day) & Q(issue_date__month=date.month) & Q(issue_date__year=date.year))
        kwargs['today_payments'] = LoanPayment.objects.filter(Q(date__day=date.day) & Q(date__month=date.month) & Q(date__year=date.year))
        kwargs['expenses'] = Expenses.objects.filter(Q(date__day=date.day) & Q(date__month=date.month) & Q(date__year=date.year))
        return super().get_context_data(**kwargs)


class MonthSummeryList(TemplateView):
    template_name = 'loans_admin/month_summery_list.html'

    def get(self, request, *args, **kwargs):
        previous_year = None
        year = None
        show_previous_year = kwargs['show_previous_year']
        if show_previous_year == 0:
            print(show_previous_year)
            year = datetime.today().year
            previous_year = year - 1
        if show_previous_year == 1:
            print('take me back in time')
            year = datetime.today().year - 1
            previous_year = year - 1
        #year = datetime.datetime.today().year
        #previous_year = year - 1
        months = []

        # show last month of last year
        last_december = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=12) &
                                         Q(date__year=previous_year))
        if last_december.count() > 0:
            months.append(('December', 12, previous_year))

        january = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=1) &
                                         Q(date__year=year))
        if january.count() > 0:
            months.append(('January', 1, year))

        february = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=2) &
                                         Q(date__year=year))
        if february.count() > 0:
            months.append(('February', 2, year))

        march = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=3) &
                                         Q(date__year=year))
        if march.count() > 0:
            months.append(('March', 3, year))

        april = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=4) &
                                         Q(date__year=year))
        if april.count() > 0:
            months.append(('April', 4, year))

        may = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=5) &
                                         Q(date__year=year))
        if may.count() > 0:
            months.append(('May', 5, year))

        june = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=6) &
                                         Q(date__year=year))
        if june.count() > 0:
            months.append(('June', 6, year))

        july = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=7) &
                                         Q(date__year=year))
        if july.count() > 0:
            months.append(('July', 7, year))

        august = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=8) &
                                         Q(date__year=year))
        if august.count() > 0:
            months.append(('August', 8, year))

        september = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=9) &
                                         Q(date__year=year))
        if september.count() > 0:
            months.append(('September', 9, year))

        october = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=10) &
                                         Q(date__year=year))
        if october.count() > 0:
            months.append(('October', 10, year))

        november = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=11) &
                                         Q(date__year=year))
        if november.count() > 0:
            months.append(('November', 11, year))

        december = Summery.objects.filter(Q(station=request.user.station)&
                                         Q(date__month=12) &
                                         Q(date__year=year))
        if december.count() > 0:
            months.append(('December', 12, year))

        return render(request, self.template_name, {'months': months, 'show_previous_year': show_previous_year})


class MonthSummeryDetail(TemplateView):
    template_name = 'loans_admin/month_summery_detail.html'

    def get(self, request, *args, **kwargs):
        month=kwargs['month']
        year=kwargs['year']
        month_name = kwargs['month_name']
        # initialize the totals
        total_payments = 0
        total_expenditure = 0
        total_pending_loans = 0
        total_active_loans = 0
        total_expected_cash = 0
        total_cash_at_hand = 0
        total_profits = 0

        # get queryset
        summaries = Summery.objects.filter(Q(date__month=month)&
                                           Q(date__year=year)&
                                           Q(station=self.request.user.station))

        loans_list = Loan.objects.filter(Q(issue_date__month=month) &
                                           Q(issue_date__year=year) &
                                           Q(station=self.request.user.station))

        payment_list = LoanPayment.objects.filter(Q(date__month=month)&
                                              Q(date__year=year)&
                                              Q(station=self.request.user.station))
        expenses_list = Expenses.objects.filter(Q(date__month=month) &
                                                   Q(date__year=year)&
                                                   Q(station=self.request.user.station))


        #Calculate Totals
        for summary in summaries:
            total_payments += summary.total_payments
            total_pending_loans += summary.total_pending_loans
            total_active_loans +=summary.total_active_loans
            total_expenditure +=summary.total_expenditure
            total_expected_cash += total_expected_cash
            total_cash_at_hand += summary.total_cash_at_hand
            total_profits +=summary.total_profits

        cash_difference = total_cash_at_hand - total_expected_cash


        context={'summaries': summaries, 'month_name': month_name, 'year': year, 'month':month,
                 'total_payments':total_payments, 'total_expenditure': total_expenditure, 'total_pending_loans': total_pending_loans,
                 'total_active_loans': total_active_loans,
                 'total_expected_cash': total_expected_cash, 'total_cash_at_hand': total_cash_at_hand, 'cash_difference': cash_difference,
                 'total_profits': total_profits, 'loans_list': loans_list, 'payment_list': payment_list, 'expenses_list': expenses_list}
        return render(request, self.template_name, context)



class IssueLoanNewCustomer(FormView):
    template_name = 'loans_admin/issue_loan.html'

    def get(self, request, *args, **kwargs):
        #new customer form
        customer_form = forms.CustomerForm()
        # new loan form
        loan_form = loans.forms.LoanForm()

        context={'customer_form': customer_form, 'loan_form': loan_form,}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #save new customer
        customer_form = forms.CustomerForm(request.POST or None)
        if customer_form.is_valid():
            customer = customer_form.save(commit=False)
            #customer.station = request.user.station
            customer.save()
        else:
            messages.error(request, 'The Customer Form Did Not Validate')
            return HttpResponseRedirect(reverse_lazy('loans_admin:new_loan_new'))

        #save new customer loan
        loan_form = loans.forms.LoanForm(request.POST or None)
        if loan_form.is_valid():
            loan = loan_form.save(commit=False)
            loan.customer = customer
            loan.issued_by = request.user
            #loan.station = request.user.station
            if loan.term == '1' or loan.term == '2':
                loan.interest_rate = 0.25
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
        loan_form = loans.forms.LoanForm()

        #get existing customers
        customers = Customer.objects.filter(is_active=True)

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
        loan_form = loans.forms.LoanForm(request.POST or None)
        if loan_form.is_valid():
            loan = loan_form.save(commit=False)
            loan.customer = customer
            loan.issued_by = request.user
            #loan.station = request.user.station
            if loan.term == '1' or loan.term == '2':
                loan.interest_rate = 0.25
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

class LoansUpdate():
    pass


class CustomerUpdate():
    pass

class SavingsView(FormView):
    template_name = 'loans_admin/savings.html'
    def get(self, request, *args, **kwargs):
        pending_savings = Deposit.objects.filter(Q(status='1'))
        #pool total
        pool_total = 0
        savings = Deposit.objects.filter(Q(status='2') | Q(status='3'))
        for saving in savings:
            pool_total += saving.amount

        #interest total
        interest_total = 0
        for saving in savings:
            interest_total += saving.interest_earned

        #number of active savings
        active_savings_count = savings.count()

        #number of spent savings
        spent_savings = 0
        spent_savings_total = 0
        for saving in savings:
            if saving.spent:
                spent_savings +=1
                spent_savings_total +=saving.amount
                spent_savings_total +=saving.interest_earned

        context = {'pending_savings': pending_savings, 'spent_savings':spent_savings,
                   'active_savings_count': active_savings_count, 'interest_total':interest_total, 'pool_total':pool_total,
                   'spent_savings_total':spent_savings_total}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #print(request.POST)
        try:
            deposit_id = request.POST.get('deposit_id')
            transaction_id = request.POST.get('txn_ID')

            deposit = Deposit.objects.get(pk=deposit_id)
            deposit.status = '2'
            deposit.transaction_id = transaction_id
            deposit.approved_by = request.user
            deposit.date_confirmed = timezone.now()
            deposit.save()
            messages.success(request, 'Deposit Confirmed')
        except Deposit.DoesNotExist:
            messages.error(request, 'I could not find the specified deposit, I plead Insanity!')
        return HttpResponseRedirect(reverse_lazy('loans_admin:savings'))