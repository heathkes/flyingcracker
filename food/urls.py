from django.conf.urls.defaults import *

urlpatterns = patterns('food.views',
    (r'^$', 'index'),
    (r'^(?P<recipe_slug>[\w_-]+)/$', 'detail'),     # recipe/slug
)
