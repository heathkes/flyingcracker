from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from fc3.weatherstation.models import Weather
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from decimal import *
import socket
import datetime
import math
from fc3.json import JsonResponse
from noaa import get_NOAA_forecast
from cbac import get_CBAC_forecast
import fc3.gchart as gchart


def get_weather_for_date(wdate):
    return Weather.objects.filter(timestamp__year=wdate.year,
                                  timestamp__month=wdate.month,
                                  timestamp__day=wdate.day).order_by('timestamp')


def today_yesterday_year_ago_weather(request):
    qs_list = []
    qs_list.append(today_weather)
    qs_list.append(yesterday_weather)
    qs_list.append(year_ago_weather)
    return qs_list

def today_weather(request):
    today = get_today(request)
    return get_weather_for_date(today)
    
def yesterday_weather(request):
    today = get_today(request)
    yesterday = today - 1
    return get_weather_for_date(yesterday)

def year_ago_weather(request):
    today = get_today(request)
    year_ago = today - 365
    return get_weather_for_date(year_ago)

def day_temp_charts(qs_list, colors):
    '''
    Accepts a list of querysets. Each queryset corresponds to a line on the chart.
    Returns a list of charts, one for each temperature unit type.
    
    '''
    data_list = []  # list of temperature unit dictionaries
    for date_qs in qs_list:
        if date_qs: # only work on this if the queryset is not empty
            data_list.append(temp_dict(date_qs))

    t_chart = [] # list of chart URLs
    for unit in temp_units:
        floor = 200
        ceil = -200
        plot_list = [] # list of plot lines, each a list of temperature values
        for t_dict in data_list:
            t_vals = t_dict[unit]
            # add list of temp values to list of plot lines
            plot_list.append(t_vals)
            # determine the lowest value seen for this unit type
            temp_list = [i for i in t_vals if i is not None]
            temp_list.append(floor)    # add lowest value so far to the list
            floor = min(temp_list)
            floor = int(math.floor(float(floor)/10.0)*10)   # round down to nearest ten degrees
            # determine the highest value seen for this unit type
            temp_list = [i for i in t_vals if i is not None]
            temp_list.append(ceil)    # add highest value so far to the list
            ceil = max(temp_list)
            ceil = int(math.ceil(float(ceil)/10.0)*10)    # round up to nearest ten degrees
                
        # create plot with all these lines
        temp_plot = weather_iphone_chart(plot_list, floor, ceil, 260, 100, colors)
        
        t_chart.append(temp_plot)
    return t_chart

def day_baro_charts(date_qs):
    '''
    Accepts a single queryset of Weather data.
    Returns a list of charts, one for each pressure unit type.
    
    '''
    b_chart = []
    b_dict = baro_dict(date_qs)
    for unit in baro_units:
        b_vals = b_dict[unit]
        floor = min((i for i in b_vals if i is not None))   # ignore Nones in the list
        b_chart.append(baro_chart(b_vals, floor, max(b_vals), 292, 120))
    return b_chart

def baro_chart(data_list, floor, ceil, width, height):
    '''
    Produce a Google Chart URL for barometric pressure from each Weather record in a list.
    '''
    if len(data_list) == 0:
        return ""
    if type(data_list[0]) == float:
        # This is typically pressure in inches so use decimal point
        floor = math.floor(float(floor)*10.0)/10.0  #round down to nearest tenth
        ceil = math.ceil(float(ceil)*10.0)/10.0   #round up to nearest tenth
    else:
        # This is typically pressure in millibars so no decimal point
        floor = int(math.floor(float(floor)/10.0)*10)   # round down to nearest ten
        ceil = int(math.ceil(float(ceil)/10.0)*10)    # round up to nearest ten
    return weather_iphone_chart([data_list], floor, ceil, width, height, ['FFCC99'])

def weather_iphone_chart(data_lists, floor, ceil, width, height, colors):
    return gchart.xchart(gchart.DAY_HOUR_DATA,
                         gchart.DAY_EVERY_3HOURS_LABELS,
                         data_lists, floor, ceil, width, height, colors
                        )

def weather_normal_chart(data_lists, floor, ceil, width, height, colors):
    return gchart.xchart(gchart.DAY_HOUR_DATA,
                         gchart.DAY_EVERY_HOUR_LABELS,
                         data_lists, floor, ceil, width, height, colors
                        )


def temp_dict(l):
    '''
    Return a dictionary of temperature lists from a list of Weather records.
    The dictionary is keyed by temp_units and each value is a list of temperatures in that unit.
    '''
    data = []
    for rec in l:
        if rec is None:
            v = None
        else:
            v = int(rec.temp)
        data.append(calc_temp_values(v))
    data = map(list, zip(*data))    # transpose the 2-dimensional array, p.161 Python Cookbook
    
    i = 0
    unit_dict = {}
    for unit in temp_units:
        unit_dict[unit] = data[i]
        i = i+1

    return unit_dict

def baro_dict(l):
    '''
    Return a list of pressure lists from a list of Weather records.
    Each list corresponds to a unit type.
    '''
    data = []
    for rec in l:
        if rec is None:
            v = None
        else:
            v = float(rec.barometer)
        data.append(calc_baro_values(v))
    data = map(list, zip(*data))    # transpose the 2-dimensional array, p.161 Python Cookbook
    
    i = 0
    unit_dict = {}
    for unit in baro_units:
        unit_dict[unit] = data[i]
        i = i+1
    return unit_dict

def get_today(request):
    if request:
        remote = request.META.get('REMOTE_ADDR')
    else:
        remote = None
    if remote is None or remote.startswith("192.168.5.") or remote.startswith("10.0.2."):  # internal testing machine
        today = datetime.date(2008,2,18)
    else:
        today = datetime.date.today()
    return today

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
        wind_dir = "wind-%s.png" % wind_dir_to_english(current.wind_dir)
        wind_dir = wind_dir.lower()
        
    today = datetime.date.today()
    if today.hour < 12:
        morning = True
    else:
        morning = False
    
    qs_list = today_yesterday_year_weather(request)
    t_chart = day_temp_charts(qs_list, ['0000FF', '87CEEB', 'BEBEBE'])
    
    date_qs = today_weather(request)
    b_chart = day_baro_charts(date_qs)
    
    cbac_forecast = get_CBAC_forecast()
    noaa_forecast = get_NOAA_forecast('CO', 12)     # Crested Butte area
    
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
            })
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        if request.GET.has_key('iui'):
            return render_to_response('weather/iphone/weather-iui.html', c)
        else:
            return render_to_response('weather/iphone/weather.html', c)
    else:
        return render_to_response('weather/current_no_ajax.html', c)


TEMP_F = 'F'
TEMP_C = 'C'
temp_units = [TEMP_F, TEMP_C]

PRESS_IN = 'in'
PRESS_MB = 'mb'
baro_units = [PRESS_IN, PRESS_MB]

speed_units = ['mph', 'kts', 'km/h', 'm/s', 'ft/s']

def calc_temp_values(value):
    '''
    Return a list of temperature values equal to the given value,
    where each value in the list corresponds with a different temperature unit.
    
    '''
    if value is not None:
        value = float(value)
    vlist = []
    for unit in temp_units:
        if value is None:
            vlist.append(None)
        else:
            if unit == TEMP_C:
                nv = (value-32)/1.8
            else:
                nv = value
            vlist.append(int(round(nv)))
    return vlist

def calc_baro_values(value):
    '''
    Return a list of pressure values equal to the given value,
    where each value in the list corresponds with a different pressure unit.
    
    '''
    if value is not None:
        value = float(value)
    vlist = []
    for unit in baro_units:
        if value is None:
            vlist.append(None)
        else:
            if unit == PRESS_MB:
                vlist.append(int(round(value*33.8639)))
            else:
                vlist.append(value)
    return vlist

def calc_temp_strings(value):
    vlist = []
    vals = calc_temp_values(value)
    for v in vals:
        vlist.append("%d" % v)
    return vlist

def calc_baro_strings(value):
    vlist = []
    vals = calc_baro_values(value)
    for v in vals:
        if type(v) == int:
            vlist.append("%d" % v)
        else:
            vlist.append("%4.2f" % v)
    return vlist

def calc_trend_strings(value):
    trend = float(value)
    vlist = []
    for unit in baro_units:
        if unit == 'mb':
            nv = int(round(trend*33.8639))
            if value > Decimal(0):
                nv = "+%d" % nv
            else:
                if value < Decimal("-0.09"):
                    nv = '<span class="warning">%d</span>' % nv
                else:
                    nv = "%d" % nv
        else:
            nv = trend
            if value > Decimal(0):
                nv = "+%3.2f" % nv
            else:
                if value < Decimal("-0.09"):
                    nv = '<span class="warning">%3.2f</span>' % nv
                else:
                    nv = "%3.2f" % nv
        vlist.append(nv)
    return vlist

def calc_speeds(value):
    value = float(value)
    vlist = []
    for unit in speed_units:
        if value == 0:
            vlist.append('Calm')
        else:
            if unit == 'kts':
                nv = value * 0.868391
            elif unit == 'km/h':
                nv = value*1.609344
            elif unit == 'm/s':
                nv = value*0.44704
            elif unit == 'ft/s':
                nv = value*1.46667
            else:
                nv = value
            vlist.append("%d" % int(round(nv)))
    return vlist

from django.template.defaultfilters import date

def current(request):
    xhr = request.GET.has_key('xhr')
    if xhr:
        # get latest weather reading
        current = Weather.objects.latest('timestamp')
        
        timestamp = date(current.timestamp, "H:i \M\T D M j,Y")

        temp_list = calc_temp_strings(current.temp)
        baro_list = calc_baro_strings(current.barometer)
        trend_list = calc_trend_strings(current.baro_trend)
        
        if int(float(current.wind_speed)) < 1:
            wind = 0
            wind_dir = None
        else:
            wind = current.wind_speed
            wind_dir = "wind-%s.png" % wind_dir_to_english(wind)
            wind_dir = wind_dir.lower()
        wind_list = calc_speeds(wind)
        
        temp_unit = request.COOKIES.get("temp_unit")
        if temp_unit is None:
            temp_unit = temp_units[0]
        baro_unit = request.COOKIES.get("baro_unit")
        if baro_unit is None:
            baro_unit = baro_units[0]
        if wind == 0:
            speed_unit = ""
            wind_units = [""]
        else:
            speed_unit = request.COOKIES.get("speed_unit")
            wind_units = speed_units
            if speed_unit is None:
                speed_unit = wind_units[0]
        
        windchill_list = calc_temp_strings(current.windchill)
        
        today = datetime.date.today()
        if today.hour < 12:
            morning = True
        else:
            morning = False

        date_qs = hourly_data(today_weather(request))
        t_chart = day_temp_chart(date_qs)
        b_chart = day_baro_chart(date_qs)
        
        response_dict = {}
        response_dict.update({'timestamp': timestamp})
        response_dict.update({'temp_units': temp_units})
        response_dict.update({'baro_units': baro_units})
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
    
    # set user preference
    
    response_dict = {}
    response_dict.update({'type': type})
    response_dict.update({'unit': unit})
    response = JsonResponse(response_dict)
    return response

dir_table = {
    'NNE': 22.5,
    'NE': 45,
    'ENE': 67.5,
    'East': 90,
    'ESE': 112.5,
    'SE': 135,
    'SSE': 157.5,
    'South': 180,
    'SSW': 202.5,
    'SW': 225,
    'WSW': 247.5,
    'West': 270,
    'WNW': 292.5,
    'NW': 315,
    'NNW': 337.5
}

def wind_dir_to_english(dir):
    for key,val in dir_table.items():
        if dir >= (val-11.25) and dir < (val+11.25):
            return key
    return 'North'

def hourly_data(qs):
    '''
    Return a list of Weather records, one for each hour.
    If an hour has no record, None is inserted in place of a record.
    '''
    hour = -1
    data = []
    for rec in qs:
        if rec.timestamp.hour > hour:
            hour = hour + 1
            while hour < rec.timestamp.hour:    # fill in missing hours with None
                data.append(None)
                hour = hour + 1
            data.append(rec)
    return data
    