from django.contrib import admin
from loans_admin.models import Summery
from loans.models import Loan

# Register your models here.
admin.site.register(Summery)
admin.site.register(Loan)

