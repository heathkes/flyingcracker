from fc3.cam.models import Cam, Category
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

def camview(request, id=None):
    if id is None:
        image = Cam.objects.get(title="Whetstone")
    else:
        image = get_object_or_404(Cam, id=id)
    list = Cam.objects.all()
    return render_to_response('cam/view.html', {'camlist': list, 'image': image})    
