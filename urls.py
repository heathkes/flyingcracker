from django.conf.urls.defaults import *

def get_static_path():
   """ Return path of /static folder relative to this file """
   import os.path
   import sys
   file = sys.modules[__name__].__file__
   return os.path.abspath(os.path.join(os.path.dirname(file), "static"))

urlpatterns = patterns('',
   (r'^admin/', include('django.contrib.admin.urls')),
   
   (r'^food/', include('fc3.food.urls'), {'recipe_type': 'F'}),
   
   (r'^cocktail/', include('fc3.food.urls'), {'recipe_type': 'D'}),
   
   (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': get_static_path() }),
)
