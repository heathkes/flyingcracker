from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _


class ScoringSystem(models.Model):
    '''
    Associated with one or more ResultPoints.
    
    '''
    name            = models.CharField('Scoring system name', max_length=100, unique=True)
    num_places      = models.PositiveIntegerField()
    
    def __unicode__(self):
        return u'%s' % self.name

    def points(self, result):
        try:
            rp = ResultPoints.objects.get(system=self, result=result)
        except ResultPoints.DoesNotExist:
            return 0
        return rp.points

class ResultPoints(models.Model):
    result          = models.CharField(max_length=50)
    points          = models.IntegerField()
    system          = models.ForeignKey(ScoringSystem)
    
    def __unicode__(self):
        return u'%s: %s=%d' % (str(self.system), self.result, self.points)

    class Meta:
        verbose_name_plural = 'Result points'