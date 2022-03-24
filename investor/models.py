from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class StriveUser(AbstractUser):
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=13, help_text='Enter Your Phone Number')
    birth_date = models.DateField(auto_created=True, null=True)
    nrc = models.CharField(max_length=15)

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

        # get interest earned

        # get total balance
        # todo all unspent deposits + interest earned

        # get cumulative balance
        cumulative_balance = 0
        for deposit in deposits:
            cumulative_balance += deposit.amount
        return cumulative_balance

class Deposit(models.Model):
    STATUS = (
        ('1','Pending Approval' ),
        ('2', 'Approved' ),
        ('3', 'Active'),
    )
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS, default='1')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    spent = models.BooleanField(default=False)

class Withdraw(models.Model):
    STATUS = (
        ('1', 'Pending Approval'),
        ('2', 'Approved'),
    )
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS, default='1')

class Interest(models.Model):
    rate = models.FloatField(blank=True, null=True)
    deposit = models.ForeignKey(Deposit, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


