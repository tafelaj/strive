from django.db import models

from investor.models import StriveUser, Station


# Create your models here.
class CustomerInstitution(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Customer(models.Model):
    SEX = (
        ('1', 'Female'),
        ('2', 'Male'),
    )
    name = models.CharField(max_length=50, help_text='Enter Full Name')
    address = models.CharField(max_length=50, help_text='Enter Address')
    phone = models.CharField(max_length=13)
    email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(help_text='Enter Customer\'s Date Of Birth (YYYY-MM-DD)', blank=True, null=True)
    nrc = models.CharField(max_length=15, help_text='Enter NRC number', blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX, help_text='Set The Customer\'s Gender')
    institution = models.ForeignKey(CustomerInstitution, help_text='Enter Customer\'s Related Institution', blank=True, null=True, on_delete=models.DO_NOTHING)
    #trading_area = models.CharField(max_length=50, help_text='Enter Customer\'s Trading Area')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    black_listed = models.BooleanField(default=False)

    def __str__(self):
        if self.nrc:
            return str(self.name) + ' ' + str(self.nrc)
        else:
            return str(self.name)


class Expenses(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    amount = models.FloatField(help_text='Enter Expense Amount')
    user = models.ForeignKey(StriveUser, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=100, help_text='What was the money used for')
    date = models.DateTimeField(auto_now_add=True)


class Summery(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    total_payments = models.FloatField(blank=True, null=True, default=0)
    balance_brought_forward = models.FloatField(blank=True, null=True)
    total_expenditure = models.FloatField(blank=True, null=True, default=0)
    total_pending_loans = models.FloatField(blank=True, null=True, default=0)
    total_active_loans = models.FloatField(blank=True, null=True, default=0)
    total_expected_cash = models.FloatField(blank=True, null=True, default=0)
    total_cash_at_hand = models.FloatField(blank=True, null=True, default=0)
    total_profits = models.FloatField(blank=True, null=True, default=0)
    date = models.DateField(auto_now_add=True)
    close_time = models.TimeField(auto_now=True)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.date) + '___' + str(self.station)

    class Meta:
        verbose_name_plural = 'Summaries'
