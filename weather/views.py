from django.shortcuts import render_to_response
from django.http import HttpResponse
from fc3.weatherstation.models import Weather
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from decimal import *
import socket
import datetime
import math


from fc3.pygooglechart import XYLineChart, Axis, ExtendedData


USI_WAN = socket.gethostbyname("usi.dyndns.org")

def google_chart(request):
    url = today_baro_chart(request, 280, 200)
    data_list, max, min = today_baro(request)
    return render_to_response('weather/plot.html', {'chart': url,
                                                    'data_list': data_list,
                                                    'max': max,
                                                    'min': min,})

def get_today(request):
    remote = request.META.get('REMOTE_ADDR')
    if remote.startswith("192.168.5.") or remote.startswith("10.0.2."):  # internal testing machine
        today = datetime.datetime(2008,2,18)
    else:
        today = datetime.datetime.today()
    today = today.replace(hour=0,minute=0,second=0,microsecond=0)
    return today
    
def today_temp_chart(request, width, height):
    data_list, max, min = today_temp(request)
    if len(data_list) == 0:
        return ""
    max = int(math.ceil(float(max)/10.0)*10)    # round up to nearest ten degrees
    min = int(math.floor(float(min)/10.0)*10)   # round down to nearest ten degrees
    chart = XYLineChart(width, height, x_range=(0,24), y_range=(min, max))
    data = data_list
    chart.add_data((0,1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24))
    chart.add_data(data)
    axis_left_index = chart.set_axis_range(Axis.LEFT, min, max)
    axis_right_index = chart.set_axis_range(Axis.RIGHT, min, max)
    axis_bottom_index = chart.set_axis_labels(Axis.BOTTOM, ['', '3a', '6a', '9a', '12', '3p', '6p', '9p', ''])
    chart.set_axis_style(axis_left_index, '909090')
    chart.set_axis_style(axis_right_index, '909090')
    chart.set_axis_style(axis_bottom_index, 'B0B0B0')
    chart.set_colours(['66CCFF'])
    chart.set_line_style(0, 3)
    return chart.get_url(ExtendedData)

def today_temp(request):
    today = get_today(request)
    qs = Weather.objects.filter(timestamp__gte=today).order_by('timestamp')
    hour = -1
    max = -100
    min = 200
    data = []
    for rec in qs:
        if hour != rec.timestamp.hour:
            hour = rec.timestamp.hour
            d = int(rec.temp)
            data.append(d)
            if d > max:
                max = d
            if d < min:
                min = d
    return data, max, min
    
def today_baro_chart(request, width, height):
    data_list, max, min = today_baro(request)
    if len(data_list) == 0:
        return ""
    max = math.ceil(float(max)*10.0)/10.0   #round up to nearest tenth
    min = math.floor(float(min)*10.0)/10.0  #round down to nearest tenth
    chart = XYLineChart(width, height, x_range=(0,24), y_range=(min, max))
    data = data_list
    chart.add_data((0,1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24))
    chart.add_data(data)
    axis_left_index = chart.set_axis_range(Axis.LEFT, min, max)
    axis_right_index = chart.set_axis_range(Axis.RIGHT, min, max)
    axis_bottom_index = chart.set_axis_labels(Axis.BOTTOM, ['', '3a', '6a', '9a', '12', '3p', '6p', '9p', ''])
    chart.set_axis_style(axis_left_index, '909090')
    chart.set_axis_style(axis_right_index, '909090')
    chart.set_axis_style(axis_bottom_index, 'B0B0B0')
    chart.set_colours(['FFCC99'])
    chart.set_line_style(0, 3)
    url = chart.get_url(ExtendedData)
    return url

def today_baro(request):
    today = get_today(request)
    qs = Weather.objects.filter(timestamp__gte=today).order_by('timestamp')
    hour = -1
    max = 20.0
    min = 40.0
    data = []
    for rec in qs:
        if hour != rec.timestamp.hour:
            hour = rec.timestamp.hour
            d=float(rec.barometer)
            data.append(d)
            if d > max:
                max = d
            if d < min:
                min = d
    return data, max, min
    
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
    
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        show_titles = request.COOKIES.get("curr_weather_show_titles")
        if show_titles == None:
            show_titles = "hidden"
        show_units = request.COOKIES.get("curr_weather_show_units")
        if show_units == None:
            show_units = "none"
        xhr = request.GET.has_key('xhr')
        if xhr:
            # Note that the current Django JSON serializer cannot serialize a single object, just a queryset.
            # Therefore we need to reference the object.__dict__ with the DjangoJSONEncoder.
            # [  We expected to be able to call simplejson.dumps(current, mimetype=...)  ]
            json = simplejson.dumps(current.__dict__, cls=DjangoJSONEncoder)
            return HttpResponse(json, mimetype='application/javascript')
        else:
            # set wind string
            if int(float(current.wind_speed)) < 1:
                wind = "Calm"
            else:
                #wind = "%s<br />%d" % (wind_dir_to_english(current.wind_dir), current.wind_speed)
                wind = "%d" % current.wind_speed
                wind_dir = "wind-%s.png" % wind_dir_to_english(current.wind_dir)
                wind_dir = wind_dir.lower()
            
            # set barometric pressure trend string
            trend = current.baro_trend
            if trend > Decimal(0):
                trend = "+%3.2f" % trend
            else:
                if trend < Decimal("-0.09"):
                    trend = '<span class="warning">%3.2f</span>' % trend
                else:
                    trend = "%3.2f" % trend
    
            if request.META.get('REMOTE_ADDR') == USI_WAN:
                indoor = current.temp_inside
            else:
                indoor = None
                
            today = datetime.datetime.today()
            if today.hour < 12:
                morning = True
            else:
                morning = False
            return render_to_response('weather/iphone.html', {'current' : current,
                                                            'wind': wind,
                                                            'wind_dir': wind_dir,
                                                            'trend': trend,
                                                            'indoor': indoor,
                                                            'morning': morning,
                                                            'show_titles': show_titles,
                                                            'show_units': show_units,
                                                            'temp_chart': today_temp_chart(request, 280, 100),
                                                            'baro_chart': today_baro_chart(request, 280, 120),})
    else:
        return render_to_response('weather/current_no_ajax.html', {'current' : current})

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