#!/usr/bin/env python
from django.contrib import admin
import fc3.blog.models as blog

admin.site.register(blog.Post, blog.PostAdmin)
