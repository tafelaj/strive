from django import forms
from loans_admin.models import Customer, Loan, LoanPayment
from investor.models import Station

class DateInput(forms.DateInput):
    input_type = 'date'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['station',]
        widgets = {'date_of_birth': DateInput()}


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ('amount', 'interest_rate', 'term', "payment_frequency",)


class LoanPaymentForm(forms.ModelForm):
    class Meta:
        model = LoanPayment
        fields = ('amount',)

StationInventoryFormSet = forms.modelformset_factory(Station, fields=('name', 'address', 'phone'), extra=2)