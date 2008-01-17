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

def weather(request):
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
        if current.wind_speed < 1.0:
            wind = "Calm"
        else:
            wind = "%s at %d mph" % (wind_dir_to_english(current.wind_dir), current.wind_speed)
        return render_to_response('weather/view.html', {'current' : current, 'wind': wind})

dir_table = {
    'NNE': 22.5,
    'NE': 45,
    'ENE': 67.5,
    'E': 90,
    'ESE': 112.5,
    'SE': 135,
    'SSE': 157.5,
    'S': 180,
    'SSW': 202.5,
    'SW': 225,
    'WSW': 247.5,
    'W': 270,
    'WNW': 292.5,
    'NW': 315,
    'NNW': 337.5
}

def wind_dir_to_english(dir):
    for key,val in dir_table.items():
        if dir >= (val-11.25) and dir < (val+11.25):
            return key
    return 'N'