from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

# Uncomment to load INSTALLED_APPS admin.py module for default AdminSite instance.
admin.autodiscover()

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
    
    (r'^',                                  include('fc3.home.urls')),
)

if settings.STATIC_URL[ :5] != 'http:':
    urlpatterns += patterns('',
        (r'^' + settings.STATIC_URL + '/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    )
