#!/usr/bin/env python
from django.contrib import admin
import fc3.weatherstation.models as weatherstation


class WeatherAdmin(admin.ModelAdmin):
    pass

admin.site.register(weatherstation.Weather, WeatherAdmin)

#!/usr/bin/env python

