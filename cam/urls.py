from django.conf.urls.defaults import *
from fc3.cam.models import Cam

urlpatterns = patterns('fc3.cam.views',
    (r'^(?P<id>\d+)/$',     'camview'),
    (r'^$',                 'camview'),
 )
