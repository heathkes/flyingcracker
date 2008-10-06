#!/usr/bin/env python
import datetime
from decimal import Decimal
from fc3.weatherstation.models import Weather
import fc3.gchart as gchart
from fc3.settings import CHART_ROOT

# chart type strings - T=today, D=yesterday, Y=year ago
CHART_TYPE_TDY = 'TDY'
CHART_TYPE_TY = 'TY'
CHART_TYPE_TD = 'TD'
CHART_TYPE_T = 'T'

def day_temp_charts(qs_list, plot_func, width, height, colors):
    '''
    Accepts a list of querysets. Each queryset corresponds to a line on the chart.
    Returns a dictionary of chart URLs, keyed by temperature unit type.
    
    '''
    data_list = []  # list of temperature unit dictionaries
    for date_qs in qs_list:
        if date_qs: # only work on this if the queryset is not empty
            data_list.append(temp_dict(date_qs))

    chart = {}    # dictionary of chart URLs, keyed by unit type
    for unit in temp_units:
        floor = 200
        ceil = -200
        plot_list = [] # list of plot lines, each a list of temperature values
        for val_dict in data_list:
            vals = val_dict[unit]
            # add list of temp values to list of plot lines
            plot_list.append(vals)
            # determine the lowest and highest values seen for this unit type
            floor = gchart.int_floor(vals, floor)
            ceil = gchart.int_ceil(vals, ceil)
        chart[unit] = plot_func(plot_list, floor, ceil, width, height, colors, [4,2,2])
    return chart

def day_baro_charts(qs_list, plot_func, width, height, colors):
    '''
    Accepts a list of querysets. Each queryset corresponds to a line on the chart.
    Returns a dictionary of chart URLs, keyed by pressure unit type.
    
    '''
    data_list = []  # list of pressure unit dictionaries
    for date_qs in qs_list:
        if date_qs: # only work on this if the queryset is not empty
            data_list.append(baro_dict(date_qs))
            
    chart = {}    # dictionary of chart URLs, keyed by unit type
    for unit in baro_units:
        floor = 1500
        ceil = 0
        plot_list = [] # list of plot lines, each a list of temperature values
        for val_dict in data_list:
            vals = val_dict[unit]
            # add list of temp values to list of plot lines
            plot_list.append(vals)
            # determine the lowest and highest values seen for this unit type
            floor = gchart.flex_floor(vals, floor)
            ceil = gchart.flex_ceil(vals, ceil)
        chart[unit] = plot_func(plot_list, floor, ceil, width, height, colors, [4,2,2])
    return chart

def temp_dict(l):
    '''
    Return a dictionary of temperature lists from a list of Weather records.
    The dictionary is keyed by temp_units and each value is a list of temperatures in that unit.
    '''
    data = []
    for rec in l:
        if rec is None or rec.temp is None:
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
        if rec is None or rec.barometer is None:
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

TEMP_F = 'F'
TEMP_C = 'C'
temp_units = [TEMP_F, TEMP_C]

PRESS_IN = 'in'
PRESS_MB = 'mb'
baro_units = [PRESS_IN, PRESS_MB]

SPEED_MPH = 'mph'
SPEED_KTS = 'kts'
SPEED_KMH = 'km/h'
SPEED_MS = 'm/s'
SPEED_FTS = 'ft/s'
speed_units = [SPEED_MPH, SPEED_KTS, SPEED_KMH, SPEED_MS, SPEED_FTS]

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

def weather_on_date(date):
    '''
    Return all Weather records for a specific date.
    
    '''
    return Weather.objects.filter(timestamp__year=date.year,
                                  timestamp__month=date.month,
                                  timestamp__day=date.day).order_by('timestamp')
    
def get_today(request=None):
    '''
    Returns a datetime.date object corresponding to today,
    unless the requesting address is local in which case
    we return a date for which our local database has weather records.
    
    '''
    if request:
        remote = request.META.get('REMOTE_ADDR')
    else:
        remote = None
    if remote is None or remote.startswith("192.168.5.") or remote.startswith("10.0.2."):  # internal testing machine
        today = datetime.datetime(2008,2,18,0,0,0)
    else:
        today = datetime.date.today()
    return today

def temp_chart_filename(unit, date, type, extra):
    return weather_chart_filename(unit, date, 'temp', type, extra)

def baro_chart_filename(unit, date, type, extra):
    return weather_chart_filename(unit, date, 'baro', type, extra)

def weather_chart_filename(unit, date, title, type, extra):
    return '%d-%02d-%02d_%s_%s_%s%s.png' % (date.year, date.month, date.day, title, unit, type, extra)

if __name__=='__main__':
    today = get_today(None)
    today_wx = weather_on_date(today)
    print gchart.hourly_data(today_wx, today)
    print gchart.halfhour_data(today_wx, today)
    