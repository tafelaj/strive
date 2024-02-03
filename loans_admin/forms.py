from django import forms

from investor.models import Station
from loans_admin.models import Customer


class DateInput(forms.DateInput):
    input_type = 'date'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['station','black_listed']
        widgets = {'date_of_birth': DateInput()}


StationInventoryFormSet = forms.modelformset_factory(Station, fields=('name', 'address', 'phone'), extra=2)