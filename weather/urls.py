from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.weather.views',
    (r'^current/$',     'current'),
    (r'^unitchange/$',  'unit_change'),
    url(r'^$',          'weather', name='fc-weather'),
)
