from django.conf.urls.defaults import *
from fc3.miniblog.models import Post

blog_dict = {
   'queryset' : Post.objects.all(),
   'date_field' : 'pub_date',
}

urlpatterns = patterns('django.views.generic',
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', 'date_based.object_detail', dict(blog_dict, slug_field='slug'), name='miniblog-detail'),
       (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', 'date_based.archive_day',   dict(blog_dict, allow_empty=True)),
       (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',                  'date_based.archive_month', dict(blog_dict, allow_empty=True)),
       (r'^(?P<year>\d{4})/$',                                      'date_based.archive_year',  dict(blog_dict, make_object_list=True, allow_empty=True)),
    url(r'^$',                                                      'date_based.archive_index', blog_dict, name='miniblog-archive'),
)

urlpatterns += patterns('fc3.miniblog.views',
    url(r'^special/$',       'special',  name='miniblog-special')
)