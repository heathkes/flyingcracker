from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.weather.views',
    (r'^current/$', 'current'),
    (r'^$', 'current'),
)
