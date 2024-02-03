from django import forms
from loans_admin.models import Customer
from loans.models import Loan, LoanPayment
from investor.models import Station

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ('amount', 'term', "payment_frequency",)


class LoanPaymentForm(forms.ModelForm):
    class Meta:
        model = LoanPayment
        fields = ('amount',)