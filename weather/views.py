from django.shortcuts import render_to_response
from django.http import HttpResponse
from fc3.weatherstation.models import Weather
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

def current_no_ajax(request):
    # get latest weather reading
    current = Weather.objects.latest('timestamp')
    
    return render_to_response('weather/current_no_ajax.html', {'current' : current})

def current(request):
    # get latest weather reading
    current = Weather.objects.latest('timestamp')
    
    xhr = request.GET.has_key('xhr')
    if xhr:
        # Note that the current Django JSON serializer cannot serialize a single object, just a queryset.
        # Therefore we need to reference the object.__dict__ with the DjangoJSONEncoder.
        # [  We expected to be able to call simplejson.dumps(current, mimetype=...)  ]
        json = simplejson.dumps(current.__dict__, cls=DjangoJSONEncoder)
        return HttpResponse(json, mimetype='application/javascript')
    else:
        return render_to_response('weather/current.html', {'current' : current})

