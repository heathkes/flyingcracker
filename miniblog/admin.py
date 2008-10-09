#!/usr/bin/env python
from django.contrib import admin
import fc3.miniblog.models as miniblog


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(miniblog.Post, PostAdmin)
