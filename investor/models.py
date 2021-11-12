from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class StriveUser(AbstractUser):
    middle_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=13)
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

class InvestorAccount(models.Model):
    user = models.ForeignKey(StriveUser, on_delete=models.CASCADE)
    current_balance = models.FloatField()