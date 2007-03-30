from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
   title = models.CharField(maxlength=100)
   slug = models.SlugField(prepopulate_from=('title',), help_text='Automatically built from the title.')
   teaser = models.TextField()
   author = models.ForeignKey(User)
   pub_date = models.DateTimeField('Date published')
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

   class Meta:
      get_latest_by = 'pub_date'
      ordering = ('-pub_date',)
