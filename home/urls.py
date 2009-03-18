from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.home.views',
    url(r'^$',          'home', name='fc-home'),
    url(r'^set/$',      'service_client_set', name='fc-set'),
    url(r'^about/$',    'about', name='fc-about'),
)
