from django.db import models
from datetime import datetime


class Post(models.Model):
    pub_date = models.DateTimeField(default=datetime.now)
    body = models.TextField()

    class Meta:
        get_latest_by = 'pub_date'
        ordering = ('-pub_date',)
