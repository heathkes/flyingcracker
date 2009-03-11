#!/usr/bin/env python
from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.fantasy.views',
    url(r'^$',                              'root', name='fantasy-root'),
    url(r'^race/(?P<id>[0-9]+)/$',          'race_detail', name='fantasy-race-detail'),
    url(r'^series/(?P<id>[0-9]+)/board/$',  'leaderboard', name='fantasy-series-leaderboard'),
    url(r'^series/(?P<id>[0-9]+)/$',        'series_detail', name='fantasy-series-detail'),
)
