#!/usr/bin/env python
from django.contrib import admin
import fc3.weather.models as weather


class ChartUrlAdmin(admin.ModelAdmin):
    unique_together = (("date", "data_type", "unit", "size", "plots"),)

admin.site.register(weather.ChartUrl, ChartUrlAdmin)

