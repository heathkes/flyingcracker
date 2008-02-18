from django.shortcuts import render_to_response
from django.http import HttpResponse
from fc3.weatherstation.models import Weather
from fc3.pygooglechart import XYLineChart, Axis
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from decimal import *
import socket
import datetime
import math


USI_WAN = socket.gethostbyname("usi.dyndns.org")

def google_chart(request):
    url = today_temp_chart()
    return render_to_response('weather/plot.html', {'chart': url})

def today_temp_chart():
    temp_list, max, min = today_temps()
    max = int(math.ceil(max/10)*10)
    min = int(math.floor(min/10)*10)
    chart = XYLineChart(280, 70, x_range=(0,24), y_range=(min, max))
    data = temp_list
    chart.add_data((0,1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24))
    chart.add_data(data)
    axis_left_index = chart.set_axis_range(Axis.LEFT, min, max)
    axis_right_index = chart.set_axis_range(Axis.RIGHT, min, max)
    axis_bottom_index = chart.set_axis_labels(Axis.BOTTOM, ['', '6a', '12', '6p', ''])
    chart.set_axis_style(axis_left_index, 'B0B0B0')
    chart.set_axis_style(axis_right_index, 'B0B0B0')
    chart.set_axis_style(axis_bottom_index, 'B0B0B0')
    chart.set_colours(['66CCFF'])
    chart.set_line_style(0, 3)
    return chart.get_url()

def today_temps():
    today = datetime.datetime(2008,2,17)    # forcing specific date for testing
    qs = Weather.objects.filter(timestamp__gte=today).order_by('timestamp')
    hour = -1
    max = -100
    min = 200
    temps = []
    for rec in qs:
        if hour != rec.timestamp.hour:
            hour = rec.timestamp.hour
            t = rec.temp
            temps.append(int(t))
            if t > max:
                max = t
            if t < min:
                min = t
    return temps, max, min
    
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
                wind = "%s<br />%d" % (wind_dir_to_english(current.wind_dir), current.wind_speed)
            
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
                
            url = today_temp_chart()
            
            return render_to_response('weather/iphone.html', {'current' : current,
                                                            'wind': wind,
                                                            'trend': trend,
                                                            'indoor': indoor,
                                                            'show_titles': show_titles,
                                                            'show_units': show_units,
                                                            'chart': url,})
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