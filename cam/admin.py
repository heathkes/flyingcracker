#!/usr/bin/env python
from django.contrib import admin
import fc3.cam.models as cam

admin.site.register(cam.Category)
admin.site.register(cam.Cam, cam.CamAdmin)
