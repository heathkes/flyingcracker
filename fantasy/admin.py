#!/usr/bin/env python
from django.contrib import admin
from django.contrib.contenttypes import generic
import fantasy.models as fantasy


class GuessAdmin(admin.ModelAdmin):
    list_display = ('series', 'event', 'username', 'competitor', 'late_entry', 'timestamp')
    list_display_links = ('competitor',)
    list_filter = ('user', 'late_entry')
    list_editable = ('late_entry',)
    
    def series(self, obj):
        return "%s" % obj.guess_for.series.__unicode__()

    def event(self, obj):
        return "%s" % obj.guess_for.__unicode__()

    def username(self, obj):
        return "%s" % obj.user.user.username
    username.short_description = 'User'
    
    def competitor(self, obj):
        return "%s" % obj.competitor
    competitor.short_description = 'Guess'
admin.site.register(fantasy.Guess, GuessAdmin)

class EventAdmin(admin.ModelAdmin):
#    list_display = ('series', )
    list_filter = ('series', )
admin.site.register(fantasy.Event, EventAdmin)

admin.site.register(fantasy.Series)
admin.site.register(fantasy.Competitor)
admin.site.register(fantasy.Result)

