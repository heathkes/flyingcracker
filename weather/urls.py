from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.weather.views',
    (r'^current/$',     'current'),
    (r'^plot/$',        'google_chart'),
    (r'^unitchange/$',  'unit_change'),
    url(r'^$',          'weather', name='weather-current'),
)
