
def media_url(request):
    from django.conf import settings
    return {'media_url': settings.MEDIA_URL}

def yui_version(request):
    from django.conf import settings
    return {'yui_version': settings.YUI_VERSION}
