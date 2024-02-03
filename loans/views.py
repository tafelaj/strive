from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from Strive.decorators import user_is_investor
from django.utils.decorators import method_decorator
from . import forms
from .models import Loan
from django.db.models import Q

@method_decorator(user_is_investor, name='get')
class Home(TemplateView):
    template_name = 'loans/loan_home.html'

    def get(self, request, *args, **kwargs):
        loans = Loan.objects.filter(Q(user=request.user) & Q(status='1') | Q(status='2'))
        context = {'loans': loans,}
        return render(request, self.template_name, context)


class RequestLoan(FormView):
    template_name = 'loans/issue_loan.html'

    def get(self, request, *args, **kwargs):
        # new loan form
        loan_form = forms.LoanForm()

        #get existing customers
        #customers = Customer.objects.filter(station=request.user.station)

        context = {'loan_form': loan_form,}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #save new customer
        #customer_id = request.POST.get('customer_id')
        #try:
        #    customer = Customer.objects.get(pk=customer_id)
        #except Customer.DoesNotExist:
        #    messages.error(request, 'Weirdly We Couldn\'t Find The Customer, Please Try Again')
        #    return HttpResponseRedirect(reverse_lazy('loans_admin:new_loan_existing'))

        #save new customer loan
        loan_form = forms.LoanForm(request.POST or None)
        if loan_form.is_valid():
            user = self.request.user
            loan = loan_form.save(commit=False)
            loan.user = user
            #loan.station = request.user.station
            loan.save()
        else:
            messages.error(request, 'The Loan Form Did Not Validate')
            return HttpResponseRedirect(reverse_lazy('loans_admin:new_loan_existing'))
        messages.success(request, 'Loan Application Recorded')
        return HttpResponseRedirect(reverse_lazy('loans:home'))