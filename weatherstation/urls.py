from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.weatherstation.views',
    (r'^upload/$', 'upload_data'),
    (r'^$', 'download_data'),
)
