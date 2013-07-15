from django.conf.urls.defaults import *
from django.views.generic import dates

from fc3.miniblog.models import Post

urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$',
        dates.DateDetailView.as_view(model=Post, date_field='pub_date'), name='miniblog-detail'),
       (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        dates.DayArchiveView.as_view(model=Post)),
       (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        dates.MonthArchiveView.as_view(model=Post)),
       (r'^(?P<year>\d{4})/$',
        dates.YearArchiveView.as_view(model=Post)),
    url(r'^$',
        dates.ArchiveIndexView.as_view(model=Post, date_field='pub_date'), name='miniblog-archive'),
)

urlpatterns += patterns('fc3.miniblog.views',
    url(r'^special/$',       'special',  name='miniblog-special')
)