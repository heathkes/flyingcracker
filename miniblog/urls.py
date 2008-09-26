from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.miniblog.views',
    url(r'^$',                             'miniblog', name='miniblog-items'),
)

