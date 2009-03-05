from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

import mobileadmin
try:
    mobileadmin.autoregister()
except:
    pass

urlpatterns = patterns('',
    # Admin URLs
    (r'^admin/doc/',                        include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)',                        admin.site.root),
    
    # Project URLs
#    (r'^comments/',                         include('django.contrib.comments.urls.comments')),
    (r'^accounts/',                         include('fc3.accounts.urls')),
    (r'^blog/',                             include('fc3.blog.urls')),
    (r'^cam/',                              include('fc3.cam.urls')),
    (r'^(?P<recipe_type>cocktail|food)/',   include('fc3.food.urls')),
    (r'^weatherstation/',                   include('fc3.weatherstation.urls')),
    (r'^weather/',                          include('fc3.weather.urls')),
    (r'^grill/',                            include('fc3.grill.urls')),
    (r'^miniblog/',                         include('fc3.miniblog.urls')),
    (r'^races/',                            include('fc3.races.urls')),
    (r'^',                                  include('fc3.home.urls')),
)

if settings.STATIC_URL[ :5] != 'http:':
    urlpatterns += patterns('django.views.static',
        (r'^' + settings.STATIC_URL + '/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT }),
    )

if hasattr(settings, 'LOCAL_URL') and hasattr(settings, 'LOCAL_ROOT'):
    urlpatterns += patterns('django.views.static',
        (r'^' + settings.LOCAL_URL + '/(?P<path>.*)$', 'serve', {'document_root': settings.LOCAL_ROOT }),
    )


# Support for mobileadmin app

urlpatterns += patterns('',
    (r'^ma/(.*)', mobileadmin.sites.site.root),
)

from mobileadmin.conf import settings as ma_settings
urlpatterns += patterns('django.views.static',
    (ma_settings.MEDIA_REGEX, 'serve', {'document_root': ma_settings.MEDIA_PATH}),
)

#
# Put the feeds stuff after all other URLs so URL resolution works!
#
from fc3.feeds import RssSiteNewsFeed, AtomSiteNewsFeed

feeds = {
    'rss': RssSiteNewsFeed,
    'atom': AtomSiteNewsFeed,
}
urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)/$',               'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)