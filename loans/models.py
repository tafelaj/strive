from django.db import models
from investor.models import StriveUser

TERMS = (
    ('1', 'One Month'),
    ('2', 'Two Months'),
    ('3', 'Three Months'),
)

INSTALLMENTS = (
    ('1', 'One Installment'),
    ('2', 'Two Installment'),
    ('3', 'Three Installment'),
)

# Create your models here.
class LoanAccount(models.Model):
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    outstanding_balance = models.FloatField()
    date = models.DateTimeField(auto_created=True)
    loan_amount = models.FloatField()
    term = models.CharField(max_length=1, choices=TERMS)
    apr = models.FloatField()

class LoanPayments(models.Model):
    loan = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_created=True)

class LoanApplications(models.Model):
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    amount = models.FloatField()
    term = models.CharField(max_length=1, choices=TERMS)
    apr = models.FloatField() # add choices to the form
    installments = models.CharField(max_length=1, choices=INSTALLMENTS)