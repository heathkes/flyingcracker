#!/usr/bin/env python
from django.contrib import admin
import fc3.cam.models as cam


class CamAdmin(admin.ModelAdmin):
    
    class Admin:
        fieldset = (
            (None, {'fields': ('title', 'url', 'category', 'description', 'state')}),
        )

admin.site.register(cam.Category)
admin.site.register(cam.Cam, CamAdmin)
