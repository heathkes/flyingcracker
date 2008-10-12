#!/usr/bin/env python
from datetime import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from fc3.json import JsonResponse
from fc3.weatherstation.models import Weather
from noaa import get_NOAA_forecast
from cbac import get_CBAC_forecast
import fc3.weather.utils as utils
from fc3.weather.models import ChartUrl

def weather(request):

    # get latest weather reading
    current = Weather.objects.latest('timestamp')
    
    agent = request.META.get('HTTP_USER_AGENT')
    show_titles = request.COOKIES.get("curr_weather_show_titles")
    if show_titles == None:
        show_titles = "hidden"
    if show_titles == "hidden":
        title_state = "false"
    else:
        title_state = "true"
    show_units = request.COOKIES.get("curr_weather_show_units")
    if show_units == None:
        show_units = "none"
    if show_units == "none":
        unit_state = "false"
    else:
        unit_state = "true"
        
    # set wind background compass
    if int(float(current.wind_speed)) < 1:
        wind_dir = None
    else:
        wind_dir = "wind-%s.png" % utils.wind_dir_to_english(current.wind_dir)
        wind_dir = wind_dir.lower()
        
    today = datetime.now()
    if today.hour < 12:
        morning = True
    else:
        morning = False
    
    cbac_forecast = get_CBAC_forecast()
    noaa_forecast = get_NOAA_forecast('CO', 12)     # Crested Butte area

    start = datetime.now()
    
    t_chart = []
    b_chart = []
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        for unit in utils.temp_units:
            t_chart.append(get_chart(date.today(), ChartUrl.DATA_TEMP, ChartUrl.SIZE_IPHONE, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))
        for unit in utils.baro_units:
            b_chart.append(get_chart(date.today(), ChartUrl.DATA_PRESS, ChartUrl.SIZE_IPHONE, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))
            
        end = datetime.now()
        td = end - start
        elapsed = td.__str__().lstrip('0:')
        
        c = RequestContext(request, {
                'current': current,
                'wind_dir': wind_dir,
                'morning': morning,
                'show_titles': show_titles,
                'show_units': show_units,
                'temp_chart': t_chart,
                'baro_chart': b_chart,
                'cbac': cbac_forecast,
                'noaa': noaa_forecast,
                'unit_state': unit_state,
                'title_state': title_state,
                'elapsed': elapsed,
                })

        if request.GET.has_key('iui'):
            return render_to_response('weather/iphone/weather-iui.html', c)
        else:
            return render_to_response('weather/iphone/weather.html', c)
    else:
        t_chart = get_chart(date.today(), ChartUrl.DATA_TEMP, ChartUrl.SIZE_NORMAL, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, utils.TEMP_F)
        b_chart = get_chart(date.today(), ChartUrl.DATA_PRESS, ChartUrl.SIZE_NORMAL, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, utils.PRESS_IN)
            
        end = datetime.now()
        td = end - start
        elapsed = td.__str__().lstrip('0:')
    
        c = RequestContext(request, {
                'current': current,
                'wind_dir': wind_dir,
                'morning': morning,
                'show_titles': show_titles,
                'show_units': show_units,
                'temp_chart': t_chart,
                'baro_chart': b_chart,
                'cbac': cbac_forecast,
                'noaa': noaa_forecast,
                'unit_state': unit_state,
                'title_state': title_state,
                'elapsed': elapsed,
                })
        return render_to_response('weather/current_no_ajax.html', c)


def current(request):
    from django.template.defaultfilters import date as date_filter

    # BUGBUG - Assuming iPhone browser - not checking for iPhone browser,
    # although at the moment only the iPhone page has a "refresh" button.
    xhr = request.GET.has_key('xhr')
    if xhr:
        # get latest weather reading
        current = Weather.objects.latest('timestamp')
        
        timestamp = date_filter(current.timestamp, "H:i \M\T D M j,Y")

        temp_list = utils.calc_temp_strings(current.temp)
        baro_list = utils.calc_baro_strings(current.barometer)
        trend_list = utils.calc_trend_strings(current.baro_trend)
        
        if int(float(current.wind_speed)) < 1:
            wind = 0
            wind_dir = None
        else:
            wind = current.wind_speed
            wind_dir = "wind-%s.png" % utils.wind_dir_to_english(wind)
            wind_dir = wind_dir.lower()
        wind_list = utils.calc_speeds(wind)
        
        temp_unit = request.COOKIES.get("temp_unit")
        if temp_unit is None:
            temp_unit = utils.TEMP_F
            
        baro_unit = request.COOKIES.get("baro_unit")
        if baro_unit is None:
            baro_unit = utils.PRESS_IN
            
        if wind == 0:
            speed_unit = ""
            wind_units = [""]
        else:
            speed_unit = request.COOKIES.get("speed_unit")
            wind_units = utils.speed_units
            if speed_unit is None:
                speed_unit = utils.SPEED_MPH
        
        windchill_list = utils.calc_temp_strings(current.windchill)
        
        today = datetime.today()
        if today.hour < 12:
            morning = True
        else:
            morning = False

        t_chart = []
        b_chart = []
        for unit in utils.temp_units:
            t_chart.append(get_chart(date.today(), ChartUrl.DATA_TEMP, ChartUrl.SIZE_IPHONE, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))
        for unit in utils.baro_units:
            b_chart.append(get_chart(date.today(), ChartUrl.DATA_PRESS, ChartUrl.SIZE_IPHONE, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))
        
        response_dict = {}
        response_dict.update({'timestamp': timestamp})
        response_dict.update({'temp_units': utils.temp_units})
        response_dict.update({'baro_units': utils.baro_units})
        response_dict.update({'speed_units': wind_units})
        response_dict.update({'temp_unit': temp_unit})
        response_dict.update({'baro_unit': baro_unit})
        response_dict.update({'speed_unit': speed_unit})
        response_dict.update({'temp': temp_list})
        response_dict.update({'baro': baro_list})
        response_dict.update({'trend': trend_list})
        response_dict.update({'wind': wind_list})
        response_dict.update({'wind_dir': wind_dir})
        response_dict.update({'windchill': windchill_list})
        response_dict.update({'humidity': current.humidity})
        response_dict.update({'temp_chart': t_chart})
        response_dict.update({'baro_chart': b_chart})
        response_dict.update({'morning': morning})
        response = JsonResponse(response_dict)
        return response

def unit_change(request):
    '''
    Set the user preference for units.
    '''
    type = request.POST.get('type')
    unit = request.POST.get('unit')
    
    # set unit preference in user profile
    # ...
    
    # return same data, just for grins
    response_dict = {}
    response_dict.update({'type': type})
    response_dict.update({'unit': unit})
    response = JsonResponse(response_dict)
    return response


from fc3.weather.models import ChartUrl

def get_chart(date, data_type, size, plots, unit):
    now = datetime.now()
    try:
        chart = ChartUrl.objects.get(date=date, data_type=data_type, size=size, plots=plots, unit=unit)
    except ChartUrl.DoesNotExist:
        # create url
        chart = ChartUrl(date=date, timestamp=now, data_type=data_type, size=size, plots=plots, unit=unit)
        chart.url = utils.create_chart_url(date, data_type, size, plots, unit)
        try:
            chart.save()
        except ChartUrl.IntegrityError: # someone else got it done first
            pass
    else:
        # recreate url if timestamp is 30 minutes older than now
        if (now - chart.timestamp) > timedelta(minutes=30):
            # re-create url
            chart.url = utils.create_chart_url(date, data_type, size, plots, unit)
            chart.timestamp = now
            chart.save()
    return chart.url