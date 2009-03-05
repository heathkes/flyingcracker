from django.conf.urls.defaults import *
from django.contrib.auth import views as authviews
from django.conf import settings
from django.core.urlresolvers import reverse

urlpatterns = patterns('', 
    url(r'^login/$',                authviews.login, {'template_name': 'login.html'}, name='accounts-login'),
    url(r'^logout/$',               authviews.logout, {'template_name': 'logout.html'}, name='accounts-logout'),
    (r'^password_change/$',         authviews.password_change),
    (r'^password_reset/$',          authviews.password_reset),
    (r'^password_reset/done/$',     authviews.password_reset_done),
)
