from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
   (r'^admin/',             include('django.contrib.admin.urls')),
   (r'^accounts/',          include('registration.urls')),
   (r'^cam/',               include('cam.urls')),
   (r'^food/',              include('fc3.food.urls'), {'recipe_type': 'F'}),
   (r'^cocktail/',          include('fc3.food.urls'), {'recipe_type': 'D'}),
   (r'^blog/',              include('fc3.blog.urls')),
   (r'^comments/',          include('django.contrib.comments.urls.comments')),
   (r'^weatherstation/',    include('fc3.weatherstation.urls')),
   (r'^weather/',           include('fc3.weather.urls')),
   (r'^$',                  include('fc3.blog.urls')),
)

if settings.STATIC_URL[ :5] != 'http:':
    urlpatterns += patterns('',
        (r'^' + settings.STATIC_URL[1: ] + '/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    )
