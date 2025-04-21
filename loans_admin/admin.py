from django.contrib import admin
from loans_admin.models import Summery, Institution, Customer
from loans.models import Loan

# Register your models here.
admin.site.register(Summery)
admin.site.register(Loan)
admin.site.register(Institution)
admin.site.register(Customer)

