from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.cam.views',
    (r'^list/$',            'cam_list'),
    (r'^image/$',           'cam_image'),
    (r'^suggest/$',         'cam_suggestion'),
    (r'^$',                 'cam_view'),
)
