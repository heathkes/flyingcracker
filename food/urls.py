from django.conf.urls.defaults import *

urlpatterns = patterns('food.views',
    (r'^$', 'index'),
    (r'^ingredient/$', 'foodstuff'),
    (r'^ingredient/(?P<foodstuff_slug>[\w_-]+)/$', 'foodstuff_detail'),
    (r'^(?P<recipe_slug>[\w_-]+)/$', 'detail'),     # recipe/slug
)
