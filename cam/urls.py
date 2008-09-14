from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.cam.views',
    url(r'^list/$',            'cam_list', name='fc-cam-list'),
    url(r'^image/$',           'cam_image', name='fc-cam-image'),
    url(r'^$',                 'cam_view', name='fc-cam'),
)
