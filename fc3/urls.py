from __future__ import absolute_import

from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings
from fc3 import views


try:
    from fc3 import pattern_views
except ImportError:
    pattern_views = None

urlpatterns = patterns('',
    # Admin URLs
    (r'^admin/doc/',                        include('django.contrib.admindocs.urls')),
    (r'^admin/',                            include(admin.site.urls)),
    (r'^comments/',                         include('django.contrib.comments.urls')),

    # Application URLs
    (r'^accounts/',                         include('registration.urls')),
#    (r'^profiles/',                         include('profiles_urls')),
#    (r'^client/',                           include('serviceclient.urls')),
    (r'^blog/',                             include('blog.urls')),
    (r'^cam/',                              include('cam.urls')),
    (r'^(?P<recipe_type>cocktail|food)/',   include('food.urls')),
    (r'^weatherstation/',                   include('weatherstation.urls')),
    (r'^weather/',                          include('weather.urls')),
    (r'^grill/',                            include('grill.urls')),
    (r'^miniblog/',                         include('miniblog.urls')),
    (r'^fantasy/',                          include('fantasy.urls')),
    (r'^',                                  include('home.urls')),
)

admin.autodiscover()

if pattern_views and settings.DEBUG:
    urlpatterns += patterns('',
        (r'^patterns/$',                        pattern_views.show_url_patterns),
    )

if settings.STATIC_URL[ :5] != 'http:':
    urlpatterns += patterns('django.views.static',
        (r'^' + settings.STATIC_URL + '(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT }),
    )

if hasattr(settings, 'LOCAL_URL') and hasattr(settings, 'LOCAL_ROOT'):
    urlpatterns += patterns('django.views.static',
        (r'^' + settings.LOCAL_URL + '/(?P<path>.*)$', 'serve', {'document_root': settings.LOCAL_ROOT }),
    )
