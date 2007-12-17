from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
   (r'^admin/',             include('django.contrib.admin.urls')),
   (r'^comments/',          include('django.contrib.comments.urls.comments')),
   
//   (r'^accounts/',          include('fc3.registration.urls')),
   (r'^cam/',               include('fc3.cam.urls')),
   (r'^food/',              include('fc3.food.urls'), {'recipe_type': 'F'}),
   (r'^cocktail/',          include('fc3.food.urls'), {'recipe_type': 'D'}),
   (r'^blog/',              include('fc3.blog.urls')),
   (r'^weatherstation/',    include('fc3.weatherstation.urls')),
   (r'^weather/',           include('fc3.weather.urls')),
   (r'^$',                  include('fc3.blog.urls')),
)

if settings.STATIC_URL[ :5] != 'http:':
    urlpatterns += patterns('',
        (r'^' + settings.STATIC_URL[1: ] + '/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    )
