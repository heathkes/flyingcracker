from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.weather.views',
    (r'^current/$', 'current_no_ajax'),
    (r'^plot/$', 'google_chart'),
    (r'^$', 'weather'),
)
