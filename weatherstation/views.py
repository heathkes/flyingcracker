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

    dateutc = request.GET.get('datemtn', None)
    if dateutc is not None:
        dateutc = dateutc.replace(':',' ').replace('-',' ').replace('+',' ')
        year,month,day,hour,minute,second = dateutc.split()
        mountain_tz = USTimeZone(-7, "Mountain", "MST", "MDT")
        timestamp = datetime(int(year),int(month),int(day),int(hour),int(minute),int(second),0,mountain_tz)
        
        wind_dir    = request.GET.get('winddir', None)
        wind_speed  = request.GET.get('windspeedmph', None)
        wind_peak   = request.GET.get('windgustmph', None)
        temp        = request.GET.get('tempf', None)
        barometer   = request.GET.get('baromin', None)
        dewpoint    = request.GET.get('dewptf', None)
        humidity    = request.GET.get('humidity', None)
        temp_inside = request.GET.get('tempinf', None)
        baro_trend  = request.GET.get('baromtrendin', None)
        windchill   = request.GET.get('windchillf', None)
        rain        = request.GET.get('rainin', None)
        station_id  = request.GET.get('ID', None)

        try:
            rec,created = Weather.objects.get_or_create(
                             timestamp = timestamp,
                             defaults = {
                                 'wind_dir': wind_dir,
                                 'wind_speed': wind_speed,
                                 'wind_peak': wind_peak,
                                 'temp': temp,
                                 'barometer': barometer,
                                 'dewpoint': dewpoint,
                                 'humidity': humidity,
                                 'temp_inside': temp_inside,
                                 'baro_trend': baro_trend,
                                 'windchill': windchill,
                                 'rain': rain,
                                 'station_id': station_id,
                             }
                            )
            if created is not True:
                # Record already exists, replace with good values and save.
                rec.wind_dir = int(wind_dir),
                rec.wind_speed = float(wind_speed),
                rec.wind_peak = float(wind_peak),
                rec.temp = float(temp),
                rec.barometer = float(barometer),
                #rec.dewpoint = dewpoint,
                rec.humidity = int(humidity),
                rec.temp_inside = float(temp_inside),
                #rec.baro_trend = baro_trend,
                rec.windchill = float(windchill),
                #rec.rain = rain,
                rec.station_id = station_id,
                rec.save()
        except:
            response=HttpResponse("failed: '%s'" % traceback.format_exc())
        else:
            response = HttpResponse("success")
    else:
        response = HttpResponse("failed: missing dateutc field in URL")
    return response
    
def download_data(request):
    pass
