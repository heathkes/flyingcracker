from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models import permalink
from datetime import date
from django.utils.translation import ugettext_lazy as _
from scoresys.models import ScoringSystem


class Series(models.Model):
    '''
    One or more races, i.e. Formula One 2009.
    
    '''
    name            = models.CharField('Series name', max_length=100, unique=True)
    start_date      = models.DateField()
    end_date        = models.DateField()
    athlete_label   = models.CharField(help_text='How are athletes referred to in this series, i.e. "Driver" or "Rider"', max_length=50, blank=True, null=True)
    invite_only     = models.BooleanField('Users must be invited')
    only_members_can_view = models.BooleanField('Only members can view results')
    users_enter_athletes = models.BooleanField('Users can add Athletes', default=True)
    scoring_system  = models.ForeignKey(ScoringSystem, blank=True, null=True)
    
    # BUGBUG - this will eventually be:
    # user_group = models.ForeignKey(UserGroup)
    owner           = models.ForeignKey(User)

    class Meta:
        verbose_name_plural = 'series'
    
    def is_admin(self, user):
        return user == self.owner
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return ('fantasy-series-detail', [self.pk])
    get_absolute_url = permalink(get_absolute_url)


class Race(models.Model):
    '''
    A portion of an race series, i.e. Monaco Grand Prix.
    
    '''
    name        = models.CharField('Race name', max_length=100)
    date        = models.DateField()
    start_time  = models.TimeField(help_text='in UTC (Greenwich time)')
    location    = models.CharField(max_length=100, blank=True, null=True)
    series      = models.ForeignKey(Series)
    
    class Meta:
        ordering = ['date']
        unique_together = ('name', 'series')

    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return ('fantasy-race-detail', [self.pk])
    get_absolute_url = permalink(get_absolute_url)


class Team(models.Model):
    name        = models.CharField(max_length=100)
    series      = models.ForeignKey(Series)
    
    class Meta:
        unique_together = ('name', 'series')
        
    def __unicode__(self):
        return u'%s' % self.name


class Athlete(models.Model):
    name        = models.CharField(max_length=100)
    team        = models.ForeignKey(Team, blank=True, null=True)
    series      = models.ForeignKey(Series)
    
    class Meta:
        unique_together = ('name', 'series')
    
    def __unicode__(self):
        return u'%s' % self.name


class Result(models.Model):
    athlete     = models.ForeignKey(Athlete)
    race        = models.ForeignKey(Race)
    place       = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['place']
        unique_together = ('athlete','race')
    
    def __unicode__(self):
        return u'%s' % self.athlete


class Guess(models.Model):
    user        = models.ForeignKey(User)   # BUGBUG - will eventually be a SCUP
    athlete     = models.ForeignKey(Athlete)
    race        = models.ForeignKey(Race)

    class Meta:
        verbose_name_plural = 'guesses'
    
    def __unicode__(self):
        return u'%s' % self.athlete

