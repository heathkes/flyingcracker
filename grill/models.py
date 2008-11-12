from django.db import models
from django.contrib.auth.models import User


class Doneness(models.Model):
    title = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.title

    
class Method(models.Model):
    title = models.CharField(max_length=20)
    description = models.TextField()
    
    def __unicode__(self):
        return self.title
    
    
class Food(models.Model):
    title = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.title
    
    
class Hardware(models.Model):
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.make + ' ' + self.model
    
    
class Cut(models.Model):
    title = models.CharField(max_length=40)
    
    def __unicode__(self):
        return self.title
    
    
class Grilling(models.Model):
    user = models.ManyToManyField(User, blank=True, null=True)
    doneness = models.ForeignKey(Doneness)
    method = models.ForeignKey(Method)
    food = models.ForeignKey(Food)
    hardware = models.ForeignKey(Hardware, blank=True, null=True)
    cut = models.ForeignKey(Cut, blank=True, null=True)
    details = models.CharField(max_length=100)
    
    def __unicode__(self):
        return ' : '.join([str(self.food), str(self.cut), str(self.doneness)]) + ' - ' + ' : '.join([str(self.hardware), str(self.method), self.details])
    