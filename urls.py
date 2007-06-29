from django.conf.urls.defaults import *
from django.conf import settings

def get_static_path():
   """ Return path of /static folder relative to this file """
   import os.path
   import sys
   file = sys.modules[__name__].__file__
   return os.path.abspath(os.path.join(os.path.dirname(file), "static"))

urlpatterns = patterns('',
   (r'^admin/',      include('django.contrib.admin.urls')),
   (r'^accounts/',   include('registration.urls')),
   (r'^food/',       include('fc3.food.urls'), {'recipe_type': 'F'}),
   (r'^cocktail/',   include('fc3.food.urls'), {'recipe_type': 'D'}),
   (r'^blog/',       include('fc3.blog.urls')),
   (r'^comments/',   include('django.contrib.comments.urls.comments')),
   (r'^weatherstation/',    include('fc3.weatherstation.urls')),
   (r'^weather/',           include('fc3.weather.urls')),
   (r'^$',           include('fc3.blog.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': get_static_path() }),
    )
