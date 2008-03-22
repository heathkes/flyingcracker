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
    
def today_temp_chart(request, width, height):
    data_list, max, min = today_temp(request)
    if len(data_list) == 0:
        return ""
    max = int(math.ceil(float(max)/10.0)*10)    # round up to nearest ten degrees
    min = int(math.floor(float(min)/10.0)*10)   # round down to nearest ten degrees
    chart = XYLineChart(width, height, x_range=(0,24), y_range=(min, max))
    data = data_list
    chart.add_data((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24))
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
    chart.add_data((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24))
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

def list_index(needle, list):
    for index,item in enumerate(list):
        if item == needle:
            return index
    return None

def next_in_list(needle, list):
    end=len(list)-1
    for index,item in enumerate(list):
        if item == needle:
            if index == end:
                return list[0]
            else:
                return list[index+1]
    return None

def weather(request):
    # get latest weather reading
    current = Weather.objects.latest('timestamp')
    
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
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
            
        cbac_forecast = CBACForecast()
        c = RequestContext(request, {
                'wind_dir': wind_dir,
                'morning': morning,
                'show_titles': show_titles,
                'show_units': show_units,
                'temp_chart': today_temp_chart(request, 280, 100),
                'baro_chart': today_baro_chart(request, 292, 120),
                'cbac': cbac_forecast,
                'unit_state': unit_state,
                'title_state': title_state,
                })
        
        return render_to_response('weather/iphone.html', c)
    else:
        return render_to_response('weather/current_no_ajax.html', {'current' : current})


temp_units = ['F', 'C']
baro_units = ['in', 'mb']
speed_units = ['mph', 'kts', 'km/h', 'm/s', 'ft/s']

def calc_temps(value):
    value = float(value)
    vlist = []
    for unit in temp_units:
        if unit == 'C':
            nv = (value-32)/1.8
        else:
            nv = value
        vlist.append("%d" % int(round(nv)))
    return vlist

def calc_baros(value):
    value = float(value)
    vlist = []
    for unit in baro_units:
        if unit == 'mb':
            vlist.append("%d" % int(round(value*33.8639)))
        else:
            vlist.append("%4.2f" % value)
    return vlist

def calc_trends(value):
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

        temp_list = calc_temps(current.temp)
        baro_list = calc_baros(current.barometer)
        trend_list = calc_trends(current.baro_trend)
        
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

        # set wind background compass
        
        windchill_list = calc_temps(current.windchill)
        
        response_dict = {}
        response_dict.update({'timestamp': timestamp})
        response_dict.update({'temp_units': temp_units})
        response_dict.update({'baro_units': baro_units})
        response_dict.update({'speed_units': wind_units})
        response_dict.update({'temp_unit': temp_unit})
        response_dict.update({'baro_unit': baro_unit})
        response_dict.update({'speed_unit': speed_unit})
        response_dict.update({'temp': temp_list})
        response_dict.update({'press': baro_list})
        response_dict.update({'trend': trend_list})
        response_dict.update({'wind': wind_list})
        response_dict.update({'wind_dir': wind_dir})
        response_dict.update({'windchill': windchill_list})
        response_dict.update({'humidity': current.humidity})
        response_dict.update({'temp_chart': today_temp_chart(request, 280, 100)})
        response_dict.update({'baro_chart': today_baro_chart(request, 292, 120)})
        response_dict.update({'test': None})
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

from xml.etree.ElementTree import XML
from xml.parsers.expat import ExpatError
import urllib
from dateutil import parser
from fc3.weatherstation.tz import USTimeZone

class CBAC:
    pubdate = ''
    synopsis = ''
    today = ''
    tonight = ''
    tomorrow = ''
    timestamp = None
    
    def __init__(self, pubdate='', synopsis='', today='', tonight='', tomorrow='', reportedby=''):
        self.synopsis = synopsis
        self.today = today
        self.tonight = tonight
        self.tomorrow = tomorrow
        self.pubdate = pubdate
        self.reportedby = reportedby
        self.timestamp = parser.parse(self.pubdate)
        mountain_tz = USTimeZone(-7, "Mountain", "MST", "MDT")
        self.timestamp = self.timestamp.astimezone(mountain_tz)
        if self.timestamp.day != datetime.today().day:
            self.stale = True
        else:
            self.stale = False
        
def CBACForecast():
    '''
    Obtain latest CBAC RSS feed
    Parse into the pieces we want (synopsis, today, tonight, tomorrow)
    Format nicely into parts
    '''
    fname = 'http://cbavalanchecenter.org/rss/'
    try:
        f = urllib.urlopen(fname)
    except IOError:
        return None
    
    try:
        xml_text = f.read()
    except IOError:
        return None
    else:
        f.close()
    
    try:
        xml = XML(xml_text)
    except ExpatError, info:
        return None;    # fail silently
    
    rss = xml
    channel = rss.find('channel')
    item = channel.find('item')
    
    # Get the data we want
    pubdate = item.findtext('pubdate')
    
    report = item.find('report')
    forecast = report.find('forecast')
    
    today = forecast.findtext('today')
    tonight = forecast.findtext('tonight')
    tomorrow = forecast.findtext('tomorrow')
    
    synopsis = report.findtext("weathersynopsis")
    
    reportedby = report.findtext("reportedby")
    
    return CBAC(pubdate, synopsis, today, tonight, tomorrow, reportedby)