from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models import permalink
from datetime import date
from django.utils.translation import ugettext_lazy as _
from scoresys.models import ScoringSystem
from serviceclient.models import ServiceClientUserProfile as SCUP


class Series(models.Model):
    '''
    One or more races, i.e. Formula One 2009.
    
    '''
    name                    = models.CharField('Series name', max_length=100, unique=True)
    description             = models.CharField(max_length=100, blank=True, null=True)
    start_date              = models.DateField()
    end_date                = models.DateField()
    competitor_label        = models.CharField(help_text='How competitors are referred to, i.e. "Driver" or "Rider".', max_length=50, blank=True, null=True)
    num_guesses             = models.PositiveIntegerField('# guesses', help_text='The number of competitors a user can pick for each race.', default=1)
    invite_only             = models.BooleanField('Users must be invited')
    only_members_can_view   = models.BooleanField('Only members can view results')
    users_enter_competitors = models.BooleanField('Users can add competitors', default=True)
    scoring_system          = models.ForeignKey(ScoringSystem, blank=True, null=True)
    
    # BUGBUG - this will eventually be:
    # user_group = models.ForeignKey(UserGroup)
    # and the creator should be an ADMIN_TYPE in that group.
    owner           = models.ForeignKey(SCUP)

    class Meta:
        verbose_name_plural = 'series'
    
    def is_admin(self, scup):
        return scup == self.owner
    
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


class Competitor(models.Model):
    name        = models.CharField(max_length=100)
    series      = models.ForeignKey(Series)
    
    class Meta:
        unique_together = ('name', 'series')
    
    def __unicode__(self):
        return u'%s' % self.name


class Result(models.Model):
    competitor  = models.ForeignKey(Competitor)
    race        = models.ForeignKey(Race)
    place       = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['place']
        unique_together = ('competitor','race')
    
    def __unicode__(self):
        return u'%s' % self.competitor

    def guessers(self):
        guessers = Guess.objects.filter(race=self.race, competitor=self.competitor)
        return [g.user for g in guessers]

class Guess(models.Model):
    user        = models.ForeignKey(SCUP)
    competitor  = models.ForeignKey(Competitor)
    race        = models.ForeignKey(Race)

    class Meta:
        verbose_name_plural = 'guesses'
    
    def __unicode__(self):
        return u'%s' % self.competitor

