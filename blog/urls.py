from django.conf.urls.defaults import *
from fc3.blog.models import Post

blog_dict = {
   'queryset' : Post.objects.all(),
   'date_field' : 'pub_date',
}

urlpatterns = patterns('django.views.generic',
    (r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\w{1,2})/(?P<slug>[0-9A-Za-z-]+)/$', 'date_based.object_detail', dict(blog_dict, month_format='%m', slug_field='slug')),
    (r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\w{1,2})/$', 'date_based.archive_day',   dict(blog_dict, month_format='%m')),
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/$',                    'date_based.archive_month', dict(blog_dict, month_format='%m')),
    (r'^(?P<year>\d{4})/$',                                     'date_based.archive_year',  dict(blog_dict, make_object_list=True)),
    (r'^/?$',                                                   'date_based.archive_index', blog_dict),
 )
