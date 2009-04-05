from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models import permalink
from datetime import date, datetime
from django.utils.translation import ugettext_lazy as _
from scoresys.models import ScoringSystem
from serviceclient.models import ServiceClientUserProfile as SCUP


class Series(models.Model):
    '''
    A series of one or more events, i.e. Formula One 2009.
    
    '''
    name                    = models.CharField('Series name', max_length=100, unique=True)
    description             = models.CharField(max_length=100, blank=True, null=True)
    start_date              = models.DateField()
    end_date                = models.DateField()
    competitor_label        = models.CharField(help_text='How competitors are referred to, i.e. "Driver" or "Rider".', max_length=50, default='Driver')
    event_label             = models.CharField(help_text='How series events are referred to, i.e. "Race" or "Stage".', max_length=50, default='Race')
    num_guesses             = models.PositiveIntegerField('# guesses', help_text='The number of competitors a user can pick for each event.', default=1)
    invite_only             = models.BooleanField('Users must be invited', default=False)
    only_members_can_view   = models.BooleanField('Only members can view results')
    users_enter_competitors = models.BooleanField('Users can add competitors', default=True)
    scoring_system          = models.ForeignKey(ScoringSystem, blank=True, null=True)
    HIDDEN_STATUS = 'H'
    ACTIVE_STATUS = 'A'
    COMPLETE_STATUS = 'C'
    STATUS_TYPES = (
        (HIDDEN_STATUS, 'HIDDEN - only admin can view'),
        (ACTIVE_STATUS, 'ACTIVE - ready for use'),
        (COMPLETE_STATUS, 'COMPLETE - series is finished'),
    )
    status                  = models.CharField(max_length=1, choices=STATUS_TYPES, default=HIDDEN_STATUS, blank=False)
    # BUGBUG - this will eventually be:
    # user_group = models.ForeignKey(UserGroup)
    # and the creator should be an ADMIN_TYPE in that group.
    owner                   = models.ForeignKey(SCUP)

    class Meta:
        verbose_name_plural = 'series'
        ordering = ('name',)
    
    def is_admin(self, scup):
        return scup == self.owner
    
    def is_hidden(self):
        return self.status == self.HIDDEN_STATUS
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return ('fantasy-series-detail', [self.pk])
    get_absolute_url = permalink(get_absolute_url)


class Event(models.Model):
    '''
    An event in a series, i.e. Monaco Grand Prix.
    
    '''
    name            = models.CharField('Event name', max_length=100)
    description     = models.CharField(max_length=100, blank=True, null=True)
    date            = models.DateField('Guess cutoff date')
    start_time      = models.TimeField('Guess cutoff time', help_text='in UTC (Greenwich time)')
    location        = models.CharField(max_length=100, blank=True, null=True)
    series          = models.ForeignKey(Series)
    result_locked   = models.BooleanField('Lock results', default=False, help_text='If unlocked, users are allowed to enter results.')
    
    class Meta:
        ordering = ['date']
        unique_together = ('name', 'series')

    def start_time_elapsed(self):
        start_time = datetime(self.date.year, self.date.month, self.date.day, self.start_time.hour, self.start_time.minute)
        return start_time < datetime.utcnow()
            
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return ('fantasy-event-detail', [self.pk])
    get_absolute_url = permalink(get_absolute_url)


class Competitor(models.Model):
    name        = models.CharField(max_length=100)
    series      = models.ForeignKey(Series)
    
    class Meta:
        unique_together = ('name', 'series')
        ordering = ['name']
    
    def __unicode__(self):
        return u'%s' % self.name


class Result(models.Model):
    competitor  = models.ForeignKey(Competitor)
    event       = models.ForeignKey(Event)
    place       = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['place']
        unique_together = ('competitor','event')
    
    def __unicode__(self):
        return u'%s: %s: %s' % (self.event, str(self.place), self.competitor)

    def guessers(self):
        guessers = Guess.objects.filter(event=self.event, competitor=self.competitor)
        return [g.user for g in guessers]

class Guess(models.Model):
    user        = models.ForeignKey(SCUP)
    competitor  = models.ForeignKey(Competitor)
    event        = models.ForeignKey(Event)

    class Meta:
        verbose_name_plural = 'guesses'
    
    def __unicode__(self):
        return u'%s: %s by %s' % (self.event, self.competitor, self.user)

