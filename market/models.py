from django.db import models
from investor.models import StriveUser

# Create your models here.
class Asset(models.Model):
    name = models.CharField(max_length=50)
    asset_type = models.CharField(max_length=1, null=True)

class AssetType(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.code

class Currency(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.code

class Pair(models.Model):
    name = models.CharField(max_length=50)
    base_currency = models.ForeignKey(AssetType , on_delete=models.CASCADE, null=True)
    qoute_currency = models.ForeignKey(Currency, on_delete=models.DO_NOTHING)
    description = models.TextField()

    def __str__(self):
        return str(self.base_currency) + '/' + str(self.qoute_currency)


class Order(models.Model):
    ORDER_TYPE = (('Buy Order','1'),('Sell Order', '2'))
    user = models.ForeignKey(StriveUser, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=1, choices=ORDER_TYPE)
    pair = models.ForeignKey(Pair, on_delete=models.DO_NOTHING)
    datetime = models.DateTimeField(auto_now_add=True)
    quantity = models.FloatField()
