from django.urls import re_path

from . import views

app_name = 'food'
urlpatterns = [
    re_path(r'^c/(?P<slug>[\w_-]+)/$', views.category_detail, name='category-detail'),
    re_path(r'^i/(?P<slug>[\w_-]+)/$', views.foodstuff_detail, name='ingredient-detail'),
    re_path(r'^ingredients/$', views.foodstuff_list, name='ingredient-list'),
    re_path(r'^(?P<slug>[\w_-]+)/$', views.recipe_detail, name='recipe-detail'),
    re_path(r'^$', views.recipe_list, name='recipe-list'),
]
