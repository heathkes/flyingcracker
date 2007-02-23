from django.conf.urls.defaults import *

urlpatterns = patterns('fc3.food.views',
    (r'^$', 'all_recipes'),
    (r'^ingredient/$', 'all_foodstuffs'),
    (r'^ingredient/(?P<slug>[\w_-]+)/$', 'foodstuff_detail'),
    (r'^(?P<slug>[\w_-]+)/$', 'recipe_detail'),     # recipe/slug
)
