from django.conf import settings

def media_url(request):
    return {'media_url': settings.MEDIA_URL}

def yui_version(request):
    yui = {}
    yui['yui_root'] = 'http://yui.yahooapis.com/'
    yui['yui_version'] = settings.YUI_VERSION
    try:
        yui['yui_path'] = settings.YUI_PATH
    except AttributeError:
        yui['yui_path'] = yui['yui_root'] + settings.YUI_VERSION
    return yui

def miniblog(request):
    from fc3.miniblog.models import Post
    posts = Post.objects.all().order_by('-pub_date')
    return {'miniblog': posts}
