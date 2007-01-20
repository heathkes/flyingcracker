from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^food/', include('fc3.food.urls'), {'recipe_type': 'F'}),
    (r'^cocktail/', include('fc3.food.urls'), {'recipe_type': 'D'}),
)
