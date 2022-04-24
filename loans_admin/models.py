from django.db import models
from investor.models import StriveUser, Station
from django.db.models import Q
# Create your models here.

class Customer(models.Model):
    SEX = (
        ('1', 'Female'),
        ('2', 'Male'),
    )
    name = models.CharField(max_length=50, help_text='Enter Full Name')
    address = models.CharField(max_length=50, help_text='Enter Address')
    date_of_birth = models.DateField(help_text='Enter Customer\'s Date Of Birth')
    nrc = models.CharField(max_length=15, help_text='Enter NRC number')
    sex = models.CharField(max_length=1, choices=SEX, help_text='Set The Customer\'s Gender')
    business_type = models.CharField(max_length=50, help_text='Enter Customer\'s Business Type')
    trading_area = models.CharField(max_length=50, help_text='Enter Customer\'s Trading Area')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name) + ' ' + str(self.nrc)


class Loan(models.Model):
    LOAN_STATUS = (
        ('1', 'Pending'),
        ('2', 'Approved'),
        ('3', 'Completed'),
    )
    LOAN_TERM = (
        ('1', 'One Month'),
        ('2', 'Two Months'),
        ('3', 'Three Months'),
    )
    PAYMENTS = (
        ('1', 'Daily'),
        ('2', 'Monthly'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    issued_by = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now=True)
    application_date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(help_text='Enter loan amount')
    interest_rate = models.FloatField(default=0.3, help_text='Enter Interest Rate As A Decimal Fraction')
    status = models.CharField(choices=LOAN_STATUS, max_length=1, default='1')
    term = models.CharField(max_length=1, choices=LOAN_TERM, default='1', help_text='Whats the term of the loan')
    payment_frequency = models.CharField(max_length=1, default='1', choices=PAYMENTS, help_text='How often will the Customer make Loan Payments')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)

    def get_total_payments(self):
        total = 0
        payments = LoanPayment.objects.filter(Q(station=self.station) &
                                              Q(loan=self.id))
        for payment in payments:
            total +=payment.amount
        return total

    def get_total_amount(self):
        # loan amount plus interest
        interest_amount = self.amount * self.interest_rate
        total = self.amount + interest_amount
        return total

    def get_balance(self):
        # calculate payments made subtract get_total_amount
        balance = self.get_total_amount() - self.get_total_payments()
        return balance

    def get_interest_percentage(self):
        percentage = str(self.interest_rate * 100)
        percentage = percentage + ' %'
        return percentage


class LoanPayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.DO_NOTHING)
    received_by = models.ForeignKey(StriveUser, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
