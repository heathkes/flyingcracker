from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

import mobileadmin
mobileadmin.autoregister()

urlpatterns = patterns('',
    (r'^admin/doc/',                        include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)',                        admin.site.root),
#    (r'^comments/',                         include('django.contrib.comments.urls.comments')),
#   (r'^accounts/',                          include('fc3.registration.urls')),
    (r'^blog/',                             include('fc3.blog.urls')),
    (r'^cam/',                              include('fc3.cam.urls')),
    (r'^(?P<recipe_type>cocktail|food)/',   include('fc3.food.urls')),
    (r'^weatherstation/',                   include('fc3.weatherstation.urls')),
    (r'^weather/',                          include('fc3.weather.urls')),
    (r'^miniblog/',                         include('fc3.miniblog.urls')),
    
    (r'^',                                  include('fc3.home.urls')),
)

urlpatterns += patterns('',
    (r'^ma/(.*)', mobileadmin.sites.site.root),
)

if settings.STATIC_URL[ :5] != 'http:':
    urlpatterns += patterns('django.views.static',
        (r'^' + settings.STATIC_URL + '/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT }),
    )

from mobileadmin.conf import settings as ma_settings

if settings.STATIC_URL[ :5] != 'http:':
    urlpatterns += patterns('django.views.static',
        (ma_settings.MEDIA_REGEX, 'serve', {'document_root': ma_settings.MEDIA_PATH}),
    )
