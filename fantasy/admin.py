#!/usr/bin/env python
from django.contrib import admin
from django.contrib.contenttypes import generic
import fc3.fantasy.models as fantasy


admin.site.register(fantasy.Series)
admin.site.register(fantasy.Event)
admin.site.register(fantasy.Competitor)
admin.site.register(fantasy.Result)
admin.site.register(fantasy.Guess)

