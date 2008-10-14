#!/usr/bin/env python
import datetime
from decimal import Decimal
from fc3.weatherstation.models import Weather
from fc3.weather.models import ChartUrl
import fc3.gchart as gchart

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

def create_chart_url(date, data_type, size, plots, unit):
    '''
    Return a chart URL for the given parameters.
    
    '''
    if type(date) == datetime.date:
        date = datetime.datetime(date.year, date.month, date.day)
        
    plot_colors = []
    qs_list = []
    
    if ChartUrl.PLOT_TODAY in plots:
        date_wx = weather_on_date(date)
        qs_list.append(gchart.hourly_data(date_wx, date))
        if data_type == ChartUrl.DATA_TEMP:
            plot_colors.append('0000FF')
        elif data_type == ChartUrl.DATA_PRESS:
            plot_colors.append('D96C00')
        else:
            plot_colors.append('000000')
    
    if ChartUrl.PLOT_YESTERDAY in plots:
        one_day = datetime.timedelta(days=1)
        yesterday = date - one_day
        yesterday_wx = weather_on_date(yesterday)
        qs_list.append(gchart.hourly_data(yesterday_wx, yesterday))
        if data_type == ChartUrl.DATA_TEMP:
            plot_colors.append('87CEEB')
        elif data_type == ChartUrl.DATA_PRESS:
            plot_colors.append('FFCC99')
        else:
            plot_colors.append('888888')

    if ChartUrl.PLOT_YEAR_AGO in plots:
        one_year = datetime.timedelta(days=365) # don't worry about leap years
        year_ago = date - one_year
        year_ago_wx = weather_on_date(year_ago)
        qs_list.append(gchart.hourly_data(year_ago_wx, year_ago))
        plot_colors.append('BEBEBE')
            
    WIDTH_DEFAULT = 300
    HEIGHT_DEFAULT = 110

    if data_type == ChartUrl.DATA_TEMP:
        if size == ChartUrl.SIZE_IPHONE:
            width = 260
            height = 100
            plot_func = gchart.day_chart_iphone
        elif size == ChartUrl.SIZE_NORMAL:
            width = 400
            height = 160
            plot_func = gchart.day_chart_normal
        else:
            width = WIDTH_DEFAULT
            height = HEIGHT_DEFAULT
            plot_func = gchart.day_chart_normal
        chart = day_temp_chart(qs_list, unit, plot_func, width, height, plot_colors)
        
    elif data_type == ChartUrl.DATA_PRESS:
        if size == ChartUrl.SIZE_IPHONE:
            width = 292
            height = 100
            plot_func = gchart.day_chart_iphone
        elif size == ChartUrl.SIZE_NORMAL:
            width = 418
            height = 160
            plot_func = gchart.day_chart_normal
        else:
            width = WIDTH_DEFAULT
            height = HEIGHT_DEFAULT
            plot_func = gchart.day_chart_normal
        chart = day_baro_chart(qs_list, unit, plot_func, width, height, plot_colors)
    else:
        return ''
    return chart.get_url()

def day_temp_chart(qs_list, unit, plot_func, width, height, colors):
    '''
    Returns a URL which plots one line for each queryset in `qs_list`.
    
    '''
    data_list = []  # list of value lists
    for date_qs in qs_list:
        if date_qs: # only work on this if the queryset is not empty
            data_list.append(convert_qs_temps(date_qs, unit))

    floor = 200
    ceil = -200
    plot_list = [] # list of plot lines, each a list of values
    for val_list in data_list:
        # add list of temp values to list of plot lines
        plot_list.append(val_list)
        # determine the lowest and highest values seen for this unit type
        floor = gchart.int_floor(val_list, floor)
        ceil = gchart.int_ceil(val_list, ceil)
    chart = plot_func(plot_list, floor, ceil, width, height, colors, [4,2,2])
    return chart

def convert_qs_temps(qs, unit):
    '''
    Returns a list of values converted to `unit` if necessary
    from a queryset of Weather records.
    
    '''
    temps = []
    for rec in qs:
        if rec is None:
            temps.append(None)
        else:
            if unit == TEMP_F:  # default units
                temps.append(round_temp(rec.temp))
            else:
                temps.append(f_to_c(rec.temp))
    return temps

def f_to_c(val):
    if val is None:
        return None
    else:
        return round_temp((float(val)-32.0)/1.8)

def round_temp(val):
    if val is None:
        return None
    else:
        return int(round(float(val)))

def day_baro_chart(qs_list, unit, plot_func, width, height, colors):
    '''
    Returns a URL which produces one line for each queryset.
    
    '''
    data_list = []  # list of value lists
    for date_qs in qs_list:
        if date_qs: # only work on this if the queryset is not empty
            data_list.append(convert_qs_pressures(date_qs, unit))
            
    floor = 1500
    ceil = 0
    plot_list = [] # list of plot lines, each a list of values
    for val_list in data_list:
        # add list of temp values to list of plot lines
        plot_list.append(val_list)
        # determine the lowest and highest values seen for this unit type
        floor = gchart.flex_floor(val_list, floor)
        ceil = gchart.flex_ceil(val_list, ceil)
    chart = plot_func(plot_list, floor, ceil, width, height, colors, [4,2,2])
    return chart

def convert_qs_pressures(qs, unit):
    '''
    Returns a list of values converted to `unit` if necessary
    from a queryset of Weather records.
    
    '''
    press = []
    for rec in qs:
        if rec is None:
            press.append(None)
        else:
            if unit == PRESS_IN:    # default units
                press.append(float(rec.barometer))
            else:
                press.append(in_to_mb(rec.barometer))
    return press

def in_to_mb(val):
    if val is None:
        return None
    else:
        return int(round(float(val)*33.8639))

def calc_temp_values(value):
    '''
    Return a list of temperature values equal to the given value,
    where each value in the list corresponds with a different temperature unit.
    
    '''
    vlist = []
    for unit in temp_units:
        if unit == TEMP_C:
            nv = f_to_c(value)
        else:
            nv = round_temp(value)
        vlist.append(nv)
    return vlist

def calc_baro_values(value):
    '''
    Return a list of pressure values equal to the given value,
    where each value in the list corresponds with a different pressure unit.
    
    '''
    vlist = []
    for unit in baro_units:
        if unit == PRESS_MB:
            vlist.append(in_to_mb(value))
        else:
            vlist.append(float(value))
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
    vlist = calc_baro_strings(value)
    if value > 0.0:
        vlist = ['+'+v for v in vlist]
    elif value < 0.09:
        vlist = ['<span class="warning">'+v+'</span>' for v in vlist]
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

def request_is_local(request):
    if request:
        remote = request.META.get('REMOTE_ADDR')
    else:
        remote = None
    if remote is None or remote.startswith("192.168.5.") or remote.startswith("10.0.2."):  # internal testing machine
        return True
    else:
        return False
    
def get_today(request=None):
    '''
    Returns a datetime.date object corresponding to today,
    unless the requesting address is local in which case
    we return a date for which our local database has weather records.
    
    '''
    if request_is_local(request):
        return datetime.date(2008,4,1)
    else:
        return datetime.date.today()

def get_today_timestamp(request=None):
    '''
    Returns a datetime.datetime object corresponding to today,
    unless the requesting address is local in which case
    we return a date for which our local database has weather records.
    
    '''
    if request_is_local(request):
        today = datetime.datetime(2008,4,1,10,11,12)
    else:
        today = datetime.now()
    return today

def temp_chart_filename(unit, date, type, extra):
    return weather_chart_filename(unit, date, 'temp', type, extra)

def baro_chart_filename(unit, date, type, extra):
    return weather_chart_filename(unit, date, 'baro', type, extra)

def weather_chart_filename(unit, date, title, type, extra):
    return '%d-%02d-%02d_%s_%s_%s%s.png' % (date.year, date.month, date.day, title, unit, type, extra)


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

if __name__=='__main__':
    today = get_today_timestamp(None)
    today_wx = weather_on_date(today)
    print gchart.hourly_data(today_wx, today)
    print gchart.halfhour_data(today_wx, today)
    