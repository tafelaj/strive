from django.db import models
from django.db.models import Q
from django.utils import timezone
from investor.models import StriveUser, Station
# Create your models here.
from loans_admin.models import Customer


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


class Loan(models.Model):
    LOAN_STATUS = (
        ('1', 'Pending'),
        ('2', 'Approved'),
        ('3', 'Completed'),
        ('4', 'Rejected'),
    )
    LOAN_TERM = (
        ('1', 'One Week'),
        ('2', 'Two Weeks'),
        ('3', 'One Month'),
        ('4', 'Two Months'),
        ('5', 'Three Months'),
    )
    PAYMENTS = (
        ('1', 'Weekly'),
        ('2', 'Monthly'),
    )
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE, related_name='customer_user', null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    approved_by = models.ForeignKey(StriveUser, on_delete=models.CASCADE, null=True, blank=True)
    issue_date = models.DateTimeField(default=timezone.now)
    application_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(default=timezone.now)
    amount = models.FloatField(help_text='Enter loan amount')
    interest_rate = models.FloatField(default=0.37, help_text='Enter Interest Rate As A Decimal Fraction')
    status = models.CharField(choices=LOAN_STATUS, max_length=1, default='1')
    term = models.CharField(max_length=1, choices=LOAN_TERM, default='1', help_text='Whats the term of the loan')
    payment_frequency = models.CharField(max_length=1, default='1', choices=PAYMENTS, help_text='How often will the Customer make Loan Payments')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    disbursed = models.BooleanField(default=False)

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

    def get_interest_amount(self):
        # loan interest
        interest_amount = self.amount * self.interest_rate
        return interest_amount

    def get_balance(self):
        # calculate payments made subtract get_total_amount
        balance = self.get_total_amount() - self.get_total_payments()
        return balance

    def get_interest_percentage(self):
        percentage = str(round(self.interest_rate * 100, 2))+ ' %'
        return percentage

    def get_loan_id(self):
        # todo refine this function so as to get a consistent number of digits in the loan ID
        loan_pk = str(self.id)
        id_length = len(loan_pk)
        if self.user:
            user_id = self.user.id
        elif self.customer:
            user_id = self.customer.id
        else:
            user_id = '0'
        # find the number of Zeros to add
        difference = 7 - id_length
        zeros = '0'
        zeros = zeros * difference
        # digits to use for the barcode
        load_id = '{}{}{}'.format(user_id, zeros, loan_pk)
        return load_id

    def __str__(self):
        user = None
        if self.user:
            user = self.user
        else:
            user = self.customer
        return str(self.get_loan_id()) + ': ' + str(user)

    def is_past_due(self):
        if timezone.now() > self.due_date:
            return True


class LoanPayment(models.Model):
    PAYMENT_TYPE = (
        ('CASH', '1'),
        ('MOBILE MONEY', '2'),
    )
    loan = models.ForeignKey(Loan, on_delete=models.DO_NOTHING)
    received_by = models.ForeignKey(StriveUser, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=1, choices=PAYMENT_TYPE, default='2')
    amount = models.FloatField()
    balance = models.FloatField(null=True, blank=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)

    def get_profits(self):
        profit = self.amount * self.loan.interest_rate
        return profit

    def __str__(self):
        return str(self.loan) + ' ' + str(self.amount)

    #def save(self, *args, **kwargs):
    #    print('saved')
    #    super().save(*args, **kwargs)