#!/usr/bin/env python
from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.races.views',
    url(r'^$',                              'root', name='races-root'),
    url(r'^race/(?P<id>[0-9]+)/$',          'race_detail', name='races-race-detail'),
    url(r'^series/(?P<id>[0-9]+)/board/$',  'leaderboard', name='races-series-leaderboard'),
    url(r'^series/(?P<id>[0-9]+)/$',        'series_detail', name='races-series-detail'),
)
