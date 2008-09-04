from django.db import models
from django.contrib import admin
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField


class Category(models.Model):
    title = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ['title']


class CamManager(models.Manager):
    
    def belongs_to_category(self, cat=None):
        '''
        Returns a queryset of all Cams associated with specified Category.
        '''
        qs = super(type(self), self).get_query_set()
        if cat:
            qs = qs.filter(category=cat)
            return qs
        else:
            return qs


class Cam(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category)
    state = USStateField(default="CO")
    objects = CamManager()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title','url',]


class CamAdmin(admin.ModelAdmin):
    
    class Admin:
        fieldset = (
            (None, {'fields': ('title', 'url', 'category', 'description', 'state')}),
        )
