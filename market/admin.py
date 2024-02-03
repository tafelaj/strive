from django.contrib import admin
from .models import Pair, Currency

# Register your models here.
admin.site.register(Pair)
#admin.site.register(Asset)
admin.site.register(Currency)
#admin.site.register(AssetType)
