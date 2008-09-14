from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from fc3.weatherstation.models import Weather
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from decimal import *
import socket
from datetime import datetime
import math
from fc3.json import JsonResponse
from fc3.pygooglechart import XYLineChart, Axis, ExtendedData, TextDataWithScaling
from noaa import get_NOAA_forecast
from cbac import get_CBAC_forecast


def today_weather(request):
    today = get_today(request)
    return Weather.objects.filter(timestamp__gte=today).order_by('timestamp')

def get_day_charts(date_qs):
    t_chart = []
    b_chart = []
    # filter the queryset to just the timestamps we want
    date_qs = hourly_data(date_qs)
    t_list = temp_list(date_qs)
    for l in t_list:
        floor = min((i for i in l if i is not None))   # ignore Nones in the list
        t_chart.append(temp_chart(l, floor, max(l), 280, 100))
        
    b_list = baro_list(date_qs)
    for l in b_list:
        floor = min((i for i in l if i is not None))   # ignore Nones in the list
        b_chart.append(baro_chart(l, floor, max(l), 292, 120))
    
    return t_chart, b_chart

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
    
def temp_chart(data_list, floor, ceil, width, height):
    '''
    Produce a Google Chart URL for temp from each Weather record in a list.
    '''
    if len(data_list) == 0:
        return ""
    floor = int(math.floor(float(floor)/10.0)*10)   # round down to nearest ten degrees
    ceil = int(math.ceil(float(ceil)/10.0)*10)    # round up to nearest ten degrees
    return weather_chart(data_list, floor, ceil, width, height, ['66CCFF'])
    
def baro_chart(data_list, floor, ceil, width, height):
    '''
    Produce a Google Chart URL for barometric pressure from each Weather record in a list.
    '''
    if len(data_list) == 0:
        return ""
    if type(data_list[0]) == float:
        floor = math.floor(float(floor)*10.0)/10.0  #round down to nearest tenth
        ceil = math.ceil(float(ceil)*10.0)/10.0   #round up to nearest tenth
    else:
        floor = int(math.floor(float(floor)/10.0)*10)   # round down to nearest ten
        ceil = int(math.ceil(float(ceil)/10.0)*10)    # round up to nearest ten
    return weather_chart(data_list, floor, ceil, width, height, ['FFCC99'])

def weather_chart(data_list, floor, ceil, width, height, colors):
    chart = XYLineChart(width, height, x_range=(0,24), y_range=(floor, ceil))
    data = data_list
    chart.add_data((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24))
    chart.add_data(data)
    axis_left_index = chart.set_axis_range(Axis.LEFT, floor, ceil)
    axis_right_index = chart.set_axis_range(Axis.RIGHT, floor, ceil)
    axis_bottom_index = chart.set_axis_labels(Axis.BOTTOM, ['', '3a', '6a', '9a', '12', '3p', '6p', '9p', ''])
    chart.set_axis_style(axis_left_index, '909090')
    chart.set_axis_style(axis_right_index, '909090')
    chart.set_axis_style(axis_bottom_index, 'B0B0B0')
    chart.set_colours(colors)
    chart.set_line_style(0, 3)
    return chart.get_url(TextDataWithScaling)
    
def temp_list(l):
    '''
    Return a list of temperature lists from a list of Weather records, one list for each unit type.
    '''
    data = []
    for rec in l:
        if rec is None:
            v = None
        else:
            v = int(rec.temp)
        data.append(calc_temp_values(v))
    data = map(list, zip(*data))    # transpose the 2-dimensional array, p.161 Python Cookbook
    return data

def baro_list(l):
    '''
    Return a list of barometric pressure lists from a list of Weather records, one for each unit type.
    '''
    data = []
    for rec in l:
        if rec is None:
            v = None
        else:
            v = float(rec.barometer)
        data.append(calc_baro_values(v))
    data = map(list, zip(*data))    # transpose the 2-dimensional array, p.161 Python Cookbook
    return data

def get_today(request):
    if request:
        remote = request.META.get('REMOTE_ADDR')
    else:
        remote = None
    if remote is None or remote.startswith("192.168.5.") or remote.startswith("10.0.2."):  # internal testing machine
        today = datetime(2008,2,18)
    else:
        today = datetime.today()
    today = today.replace(hour=0,minute=0,second=0,microsecond=0)
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
        
    today = datetime.today()
    if today.hour < 12:
        morning = True
    else:
        morning = False
    
    date_qs = today_weather(request)
    t_chart, b_chart = get_day_charts(date_qs)
    
    cbac_forecast = get_CBAC_forecast()
    noaa_forecast = get_NOAA_forecast('CO', 12)     # Crested Butte area
    
    #if self.timestamp.day != datetime.today().day:
    #    self.stale = True
    #else:
    #    self.stale = False
    
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


temp_units = ['F', 'C']
baro_units = ['in', 'mb']
speed_units = ['mph', 'kts', 'km/h', 'm/s', 'ft/s']

def calc_temp_values(value):
    if value is not None:
        value = float(value)
    vlist = []
    for unit in temp_units:
        if value is None:
            vlist.append(None)
        else:
            if unit == 'C':
                nv = (value-32)/1.8
            else:
                nv = value
            vlist.append(int(round(nv)))
    return vlist

def calc_baro_values(value):
    if value is not None:
        value = float(value)
    vlist = []
    for unit in baro_units:
        if value is None:
            vlist.append(None)
        else:
            if unit == 'mb':
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
        
        today = datetime.today()
        if today.hour < 12:
            morning = True
        else:
            morning = False

        date_qs = today_weather(request)
        t_chart, b_chart = get_day_charts(date_qs)
        
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
