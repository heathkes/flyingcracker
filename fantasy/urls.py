#!/usr/bin/env python
from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.fantasy.views',
    url(r'^$',                                      'root', name='fantasy-root'),
    url(r'^series/add/$',                           'series_edit', name='fantasy-series-add'),
    url(r'^series/(?P<id>[0-9]+)/$',                'series_detail', name='fantasy-series-detail'),
    url(r'^series/(?P<id>[0-9]+)/edit/$',           'series_edit', name='fantasy-series-edit'),
    url(r'^series/(?P<id>[0-9]+)/leaderboard/$',    'leaderboard', name='fantasy-series-leaderboard'),
    
    url(r'^series/(?P<id>[0-9]+)/athlete/list/$',   'athlete_list', name='fantasy-athlete-list'),
    url(r'^series/(?P<id>[0-9]+)/athlete/add/$',    'athlete_add', name='fantasy-athlete-add'),
    url(r'^athlete/(?P<id>[0-9]+)/edit/$',          'athlete_edit', name='fantasy-athlete-edit'),

    url(r'^series/(?P<id>[0-9]+)/race/add/$',       'race_add', name='fantasy-race-add'),
    url(r'^race/(?P<id>[0-9]+)/$',                  'race_detail', name='fantasy-race-detail'),
    url(r'^race/(?P<id>[0-9]+)/edit/$',             'race_edit', name='fantasy-race-edit'),
    url(r'^race/(?P<id>[0-9]+)/result/$',           'race_result', name='fantasy-race-result'),
    url(r'^race/(?P<id>[0-9]+)/result/edit/$',      'result_edit', name='fantasy-result-edit'),
)
