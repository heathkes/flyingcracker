from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^fc3/', include('fc3.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^cocktail/$', 'fc3.food.views.index'),
    (r'^cocktail/(?P<recipe_slug>[\w_-]+)/$', 'fc3.food.views.detail'),     # recipe/slug

)
