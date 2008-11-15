from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.grill.views',
    url(r'^d/(?P<slug>[\w_-]+)/$',      'doneness_detail', name='grill-doneness-detail'),
    url(r'^$',                          'grill', name='grill'),
)

