#!/usr/bin/env python
from django.contrib import admin
import blog.models as blog
from fc3.settings import YUI_VERSION


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'author', 'pub_date']
    search_fields = ['title', 'body']
    date_hierarchy = 'pub_date'
    
    class Media:
#        js = ['/static/js/tiny_mce/tiny_mce.js', '/static/js/textareas.js']      
        js = (
            # Utility dependencies
            'http://yui.yahooapis.com/'+YUI_VERSION+'/build/yahoo-dom-event/yahoo-dom-event.js',
            'http://yui.yahooapis.com/'+YUI_VERSION+'/build/element/element-beta-min.js',
            # Needed for Menus, Buttons and Overlays used in the RTE Toolbar
            'http://yui.yahooapis.com/'+YUI_VERSION+'/build/container/container_core-min.js',
            'http://yui.yahooapis.com/'+YUI_VERSION+'/build/menu/menu-min.js',
            'http://yui.yahooapis.com/'+YUI_VERSION+'/build/button/button-beta-min.js',
            # Source file for Rich Text Editor
            'http://yui.yahooapis.com/'+YUI_VERSION+'/build/editor/editor-beta-min.js',
            # Source file for Connection Manager
#            'http://yui.yahooapis.com/'+YUI_VERSION+'/build/connection/connection-min.js',
            '/static/js/yui/connection-debug.js',
            # Required for YUI Logger
            'http://yui.yahooapis.com/'+YUI_VERSION+'/build/logger/logger-min.js',
            # Enable console logging
            '/static/js/console-logger.js',
            # Image uploader code
            '/static/js/yui-image-uploader.js',
            # Invoke the RTE
            '/static/js/yuitextareas.js',
            )

admin.site.register(blog.Post, PostAdmin)
