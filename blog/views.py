from django.http import HttpResponse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

def upload_file(request):
    xhr = request.GET.has_key('xhr')
    if xhr and request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            # Other data on the request.FILES dictionary:
            filesize = len(file['content'])
            filetype = file['content-type']
            filename = file['filename']

            filepath ='%s/%s' % (settings.MEDIA_ROOT, filename)
            fd = open(filepath, 'wb')
            fd.write(file['content'])
            fd.close()
            fileurl = '%s/%s' % (settings.MEDIA_URL, filename)
            result = {"status": "UPLOADED", "image_url": fileurl}
        else:
            result = {"status": "upload failed"}
            
        json = simplejson.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json, mimetype='text/html')  # try mimetype='application/javascript'
    else:
        return HttpResponse('sorry')
