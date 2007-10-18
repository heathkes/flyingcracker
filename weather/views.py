from django.shortcuts import render_to_response
from django.http import HttpResponse
from fc3.weatherstation.models import Weather
from django.utils import simplejson

def current(request):
    # get latest weather reading
    current = Weather.objects.latest('timestamp')
    
    xhr = request.GET.has_key('xhr')
    if xhr:
        return HttpResponse(simplejson.dumps(current), mimetype='application/javascript')
    else:
        return render_to_response('weather/current.html', {'current' : current})
