from django.db import models
from datetime import *

class Weather(models.Model):
    station_id = models.CharField(maxlength=10)
    timestamp = models.DateTimeField('Date of reading', unique=True)
   
    wind_dir = models.IntegerField()
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2)
    wind_peak = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.IntegerField()
    temp = models.DecimalField(max_digits=5, decimal_places=2)
    rain = models.DecimalField(max_digits=4, decimal_places=2)
    barometer = models.DecimalField(max_digits=4, decimal_places=2)
    dewpoint = models.DecimalField(max_digits=4, decimal_places=2)
    temp_inside = models.DecimalField(max_digits=5, decimal_places=2)
    baro_trend = models.DecimalField(max_digits=3, decimal_places=2)
    windchill = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        if self.timestamp is not None:
            return datetime.ctime(self.timestamp)
        else:
            return "no time"

    class Meta:
        ordering = ['-timestamp']
        
    class Admin:
        # Admin options go here
        pass