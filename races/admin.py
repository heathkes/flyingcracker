#!/usr/bin/env python
from django.contrib import admin
from django.contrib.contenttypes import generic
import fc3.races.models as races


admin.site.register(races.Series)
admin.site.register(races.Race)
admin.site.register(races.Team)
admin.site.register(races.Athlete)
admin.site.register(races.Result)
admin.site.register(races.Guess)

