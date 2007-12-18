from django.conf.urls.defaults import *
from fc3.cam.models import Cam

urlpatterns = patterns('fc3.cam.views',
    (r'^cam_list/$',        'cam_list'),
    (r'^(?P<id>\d+)/$',     'cam_view'),
    (r'^$',                 'cam_view'),
)
