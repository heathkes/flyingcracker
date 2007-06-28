from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from fc3.weatherstation.models import Weather
import traceback
from datetime import datetime
from fc3.weatherstation.tz import USTimeZone

def upload_data(request):
    """
    Upload weather data view.

    Templates: ``<app_label>/weather_action.html``
    Context:
        none
    """

    try:
        dateutc = request.GET.get('datemtn')
        dateutc = dateutc.replace(':',' ').replace('-',' ').replace('+',' ')
        year,month,day,hour,minute,second = dateutc.split()
        mountain_tz = USTimeZone(-7, "Mountain", "MST", "MDT")
        timestamp = datetime(int(year),int(month),int(day),int(hour),int(minute),int(second),0,mountain_tz)
        
        rec = Weather.objects.create(
                         wind_dir = request.GET.get('winddir'),
                         wind_speed = request.GET.get('windspeedmph'),
                         wind_peak = request.GET.get('windgustmph'),
                         temp = request.GET.get('tempf'),
                         barometer = request.GET.get('baromin'),
                         dewpoint = request.GET.get('dewptf'),
                         humidity = request.GET.get('humidity'),
                         temp_inside = request.GET.get('tempinf'),
                         baro_trend = request.GET.get('baromtrendin'),
                         windchill = request.GET.get('windchillf'),
                         rain = request.GET.get('rainin'),
                         timestamp = timestamp,
                         station_id = request.GET.get('ID'),
                        )
    except:
        response=HttpResponse("failed: '%s'" % traceback.format_exc())
    else:
        response = HttpResponse("success")
    return response
    
def download_data(request):
    pass
