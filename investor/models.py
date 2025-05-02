from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class Institution(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Station(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    available_funds = models.FloatField(default=0)
    working_capital = models.FloatField(default=0)


    def __str__(self):
        return str(self.name) + ' ' + str(self.address)

class StriveUser(AbstractUser):
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=13, help_text='Enter Your Phone Number')
    birth_date = models.DateField(auto_created=True, null=True)
    nrc = models.CharField(max_length=15)
    loans_admin = models.BooleanField(default=False)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, blank=True)
    paying_account = models.CharField(max_length=20, null=True, blank=True)

    def get_full_name(self):
        """
        Return the first_name and middle name plus the last_name, with a space in between.
        """
        if self.middle_name:
            full_name = '%s %s %s' % (self.first_name, self.middle_name, self.last_name)
        else:
            full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name

    def __str__(self):
        return self.get_full_name()

class Account(models.Model):
    ACCOUNT_TYPES = (('Savings', '1'),
                     ('Asset', '2'),)
    account_type = models.CharField(max_length=1, choices=ACCOUNT_TYPES, default='1')
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)

    def get_savings_total(self):
        # get all deposits
        deposits = Deposit.objects.filter(models.Q(account=self.id) & models.Q(spent=False))

        # get cumulative balance
        cumulative_balance = 0
        for deposit in deposits:
            cumulative_balance += deposit.amount

        # get interest earned
        interest = 0
        for deposit in deposits:
            interest += deposit.interest_earned

        # get total balance
        # todo all unspent deposits + interest earned
        total_balance = cumulative_balance + interest

        return [cumulative_balance, total_balance]

class Deposit(models.Model):
    STATUS = (
        ('1','Pending Approval' ),
        ('2', 'Approved' ),
        ('3', 'Active'),
        ('4', 'Withdrawn'),
    )
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS, default='1')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    spent = models.BooleanField(default=False)
    interest_earned = models.FloatField(default=0)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    approved_by = models.ForeignKey(StriveUser, on_delete=models.CASCADE, related_name='approved_by', null=True, blank=True)
    date_confirmed = models.DateTimeField(default=timezone.now)

class Withdraw(models.Model):
    STATUS = (
        ('1', 'Pending Approval'),
        ('2', 'Approved'),
        ('3', 'Disbursed'),
    )
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS, default='1')

class Interest(models.Model):
    rate = models.FloatField(blank=True, null=True)
    deposit = models.ForeignKey(Deposit, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


