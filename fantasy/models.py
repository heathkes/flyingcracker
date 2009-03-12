from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models import permalink
from datetime import date
from django.utils.translation import ugettext_lazy as _


class Series(models.Model):
    '''
    One or more races, i.e. Formula One 2009.
    
    '''
    name            = models.CharField(max_length=100, unique=True)
    start_date      = models.DateField()
    end_date        = models.DateField()
    athlete_label   = models.CharField(max_length=50, blank=True, null=True)
    owner           = models.ForeignKey(User)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return ('fantasy-series-detail', [self.pk])
    get_absolute_url = permalink(get_absolute_url)

    class Meta:
        verbose_name_plural = 'series'


class Race(models.Model):
    '''
    A portion of an race series, i.e. Monaco Grand Prix.
    
    '''
    name        = models.CharField(max_length=100, unique=True, db_index=True)
    race_date   = models.DateField()
    race_time   = models.TimeField()
    location    = models.CharField(max_length=100, blank=True, null=True)
    series      = models.ForeignKey(Series)
    
    class Meta:
        ordering = ['race_date']
        
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return ('fantasy-race-detail', [self.pk])
    get_absolute_url = permalink(get_absolute_url)


class Team(models.Model):
    name        = models.CharField(max_length=100, unique=True, db_index=True)
    
    def __unicode__(self):
        return u'%s' % self.name


class Athlete(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    team        = models.ForeignKey(Team, blank=True, null=True)
    series      = models.ManyToManyField(Series)
    
    def __unicode__(self):
        return u'%s' % self.name


class Result(models.Model):
    athlete     = models.ForeignKey(Athlete)
    race        = models.ForeignKey(Race)
    place       = models.PositiveIntegerField()
    
    def __unicode__(self):
        return u'%s' % self.athlete
    
    class Meta:
        ordering = ['place']


class Guess(models.Model):
    user        = models.ForeignKey(User)
    athlete     = models.ForeignKey(Athlete)
    race        = models.ForeignKey(Race)
    
    def __unicode__(self):
        return u'%s' % self.athlete

    class Meta:
        verbose_name_plural = 'guesses'

