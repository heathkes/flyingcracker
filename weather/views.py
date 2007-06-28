from django.shortcuts import render_to_response
from fc3.weatherstation.models import Weather

def current(request):
    # get latest weather reading
    current = Weather.objects.latest('timestamp')
    return render_to_response('weather/current.html', {'current' : current})
