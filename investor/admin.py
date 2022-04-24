from django.contrib import admin
from investor.models import StriveUser, Institution, Station

# Register your models here.
admin.site.register(StriveUser)
admin.site.register(Institution)
admin.site.register(Station)