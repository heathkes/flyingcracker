from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(maxlength=100)
    slug = models.SlugField(prepopulate_from=('title',), help_text='Automatically built from the title.')
    teaser = models.TextField()
    author = models.ForeignKey(User)
    pub_date = models.DateTimeField('Date this post will get published')
    body = models.TextField()
    enable_comments = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
   
    def get_absolute_url(self):
        return "/blog/%s/%s/" % (self.pub_date.strftime("%Y/%m/%d").lower(), self.slug)

    class Admin:
        list_display = ('title', 'author', 'pub_date',)
        search_fields = ('title', 'body',)
        date_hierarchy = 'pub_date'
        js = ['/static/js/tiny_mce/tiny_mce.js', '/static/js/textareas.js']      

    class Meta:
        get_latest_by = 'pub_date'
        ordering = ('-pub_date',)

    def unused(self):
        js = (
            # Utility dependencies
            '/static/js/yui/yahoo-debug.js',
            'http://yui.yahooapis.com/2.3.1/build/yahoo-dom-event/yahoo-dom-event.js',
            'http://yui.yahooapis.com/2.3.1/build/dragdrop/dragdrop-min.js',
            '/static/js/yui/element-beta-debug.js',
            # Needed for Menus, Buttons and Overlays used in the RTE Toolbar
            '/static/js/yui/container_core-debug.js',
            '/static/js/yui/menu-debug.js',
            '/static/js/yui/button-beta-debug.js',
            # Source file for Rich Text Editor
            '/static/js/yui/editor-beta-min.js',
      )
