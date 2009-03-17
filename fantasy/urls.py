#!/usr/bin/env python
from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.fantasy.views',
    url(r'^$',                                      'root', name='fantasy-root'),
    url(r'^series/add/$',                           'series_edit', name='fantasy-series-add'),
    url(r'^series/(?P<id>[0-9]+)/$',                'series_detail', name='fantasy-series-detail'),
    url(r'^series/(?P<id>[0-9]+)/edit/$',           'series_edit', name='fantasy-series-edit'),
    url(r'^series/(?P<id>[0-9]+)/leaderboard/$',    'leaderboard', name='fantasy-series-leaderboard'),
    
    url(r'^series/(?P<id>[0-9]+)/competitor/list/$',   'competitor_list', name='fantasy-competitor-list'),
    url(r'^series/(?P<id>[0-9]+)/competitor/add/$',    'competitor_add', name='fantasy-competitor-add'),
    url(r'^competitor/(?P<id>[0-9]+)/edit/$',          'competitor_edit', name='fantasy-competitor-edit'),
    url(r'^competitor/(?P<id>[0-9]+)/delete/$',        'competitor_delete', name='fantasy-competitor-delete'),

    url(r'^series/(?P<id>[0-9]+)/race/add/$',       'race_add', name='fantasy-race-add'),
    url(r'^race/(?P<id>[0-9]+)/$',                  'race_detail', name='fantasy-race-detail'),
    url(r'^race/(?P<id>[0-9]+)/edit/$',             'race_edit', name='fantasy-race-edit'),
    url(r'^race/(?P<id>[0-9]+)/delete/$',           'race_delete', name='fantasy-race-delete'),
    url(r'^race/(?P<id>[0-9]+)/result/$',           'race_result', name='fantasy-race-result'),
    url(r'^race/(?P<id>[0-9]+)/result/edit/$',      'result_edit', name='fantasy-result-edit'),
)
