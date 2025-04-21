from django import forms

from investor.models import Station
from loans_admin.models import Customer


class DateInput(forms.DateInput):
    input_type = 'date'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['black_listed', 'is_active']
        widgets = {'date_of_birth': DateInput()}


StationInventoryFormSet = forms.modelformset_factory(Station, fields=('name', 'address', 'phone'), extra=2)
CustomerFormSet = forms.modelformset_factory(Customer, fields=('name', 'address', 'phone', 'email', 'date_of_birth', 'nrc', 'sex', 'institution', 'is_active', 'black_listed'), extra=5, can_delete=True)