from django import forms
from django.contrib.auth.forms import UserCreationForm
from investor.models import StriveUser

class DateInput(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = StriveUser
        fields = (
        'first_name', 'middle_name', 'last_name', 'email', 'phone', 'address', 'birth_date',
        'nrc', 'password1', 'password2',)
        widgets = {'birth_date': DateInput()}
