from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^cocktail/', include('fc3.food.urls')),
)
