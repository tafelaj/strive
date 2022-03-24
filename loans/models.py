from django.db import models
from investor.models import StriveUser


# Create your models here.
class LoanAccount(models.Model):
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    outstanding_balance = models.FloatField() #principle - payment
    date = models.DateTimeField(auto_created=True)
    principle_amount = models.FloatField()
    apr = models.FloatField()

    def get_interest_amount(self):
        if self.outstanding_balance > 0:
            amount = self.outstanding_balance * self.apr
        else:
            amount = self.principle_amount * self.apr
        return amount

    def get_loan_total(self):
        if self.outstanding_balance > 0:
            total = self.outstanding_balance + self.get_interest_amount()
        else:
            total = self.principle_amount + self.get_interest_amount()
        return total

class LoanPayments(models.Model):
    loan = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_created=True)

class LoanApplications(models.Model):
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    amount = models.FloatField()
    apr = models.FloatField() # add choices to the form