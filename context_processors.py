
def media_url(request):
    from django.conf import settings
    return {'media_url': settings.MEDIA_URL}

def yui_version(request):
    from django.conf import settings
    return {'yui_version': settings.YUI_VERSION}

def newsblog(request):
    from fc3.newsblog.models import Post
    posts = Post.objects.all().order_by('-pub_date')
    return {'newsblog': posts}
