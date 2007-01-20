from django.conf.urls.defaults import *

urlpatterns = patterns('food.views',
    (r'^$', 'all_recipes'),
    (r'^ingredient/$', 'foodstuff'),
    (r'^ingredient/(?P<slug>[\w_-]+)/$', 'foodstuff_detail'),
    (r'^(?P<slug>[\w_-]+)/$', 'recipe_detail'),     # recipe/slug
)
