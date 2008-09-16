#!/usr/bin/env python
from django.contrib import admin
import fc3.newsblog.models as news


class PostAdmin(admin.ModelAdmin):
    pass

admin.site.register(news.Post, PostAdmin)
