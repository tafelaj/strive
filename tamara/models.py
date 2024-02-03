from django.db import models

# Create your models here.
class Car(models.Model):
    VEHICLE_TYPES = (('1', 'Coupe'),('2', "SUV"), ('3', 'Bus'))
    name = models.CharField(max_length=200)
    engine_capacity = models.FloatField()
    color = models.CharField(max_length=200)
    type = models.CharField(max_length=1, choices=VEHICLE_TYPES)
    #etc