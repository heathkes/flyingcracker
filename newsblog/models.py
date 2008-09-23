from django.db import models
from datetime import datetime
from django.template.defaultfilters import truncatewords


class Post(models.Model):
    pub_date = models.DateTimeField(default=datetime.now)
    body = models.TextField()

    def __unicode__(self):
        return str(pub_date) + ' -  "' + truncatewords(body, 10) + '"'
    
    class Meta:
        get_latest_by = 'pub_date'
        ordering = ('-pub_date',)
