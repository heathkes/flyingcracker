#!/usr/bin/env python
import datetime, math
from pygooglechart import XYLineChart, Axis

DAY_EVERY_HOUR_DATA = [i for i in range(0, 24+1)]
DAY_EVERY_HALFHOUR_DATA = [i for i in range(0, (24*2)+1)]
DAY_EVERY_10_MINUTES_DATA = [i for i in range(0, (24*6)+1)]
DAY_EVERY_3HOURS_LABELS = ['', '3a', '6a', '9a', '12', '3p', '6p', '9p', '']
DAY_EVERY_HOUR_LABELS = ['', '1a', '2a', '3a', '4a', '5a', '6a', '7a', '8a', '9a', '10a', '11a', '12',
                         '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', '10p', '11p', '']

def xchart(x_data, x_labels, data_lists, y_floor, y_ceil, width, height, colors, line_widths):
    '''
    Returns the URL for a chart where all datasets use the same X-axis values.
    Y-axis labels are shown on both sides of the graph.
    
    '''
    data_list = [i for i in x_data if i is not None]
    x_floor = min(data_list)
    x_ceil = max(data_list)
    chart = XYLineChart(width, height, x_range=(x_floor, x_ceil), y_range=(y_floor, y_ceil))
    for data in data_lists:
        chart.add_data(x_data)
        chart.add_data(data)
    axis_left_index = chart.set_axis_range(Axis.LEFT, y_floor, y_ceil)
    axis_right_index = chart.set_axis_range(Axis.RIGHT, y_floor, y_ceil)
    axis_bottom_index = chart.set_axis_labels(Axis.BOTTOM, x_labels)
    chart.set_axis_style(axis_left_index, '909090')
    chart.set_axis_style(axis_right_index, '909090')
    chart.set_axis_style(axis_bottom_index, 'B0B0B0')
    chart.set_colours(colors)
    index = 0
    for width in line_widths:
        chart.set_line_style(index, width)
        index += 1
    return chart

def day_chart_iphone(data_lists, floor, ceil, width, height, colors, line_widths):
    '''
    Returns URL for a chart which expects 24 data points, one for each hour.
    X-axis labels are the hour of day every three hours.
    
    '''
    return xchart(DAY_EVERY_HOUR_DATA,
                  DAY_EVERY_3HOURS_LABELS,
                  data_lists, floor, ceil, width, height, colors, line_widths
                 )

def day_chart_normal(data_lists, floor, ceil, width, height, colors, line_widths):
    '''
    Returns URL for a chart which expects 24*2 data points, one for every half hour.
    X-axis labels are the hour of day every hour.
    
    '''
    return xchart(DAY_EVERY_HALFHOUR_DATA,
                  DAY_EVERY_HOUR_LABELS,
                  data_lists, floor, ceil, width, height, colors, line_widths
                 )

def periodic_records(qs, start, interval, periods):
    '''
    Returns a list of arbitrary type records (containing attribute 'timestamp')
    with one record for each 'interval' (i.e. 1 day) for a total of 'periods' intervals
    beginning at 'start'. If a record is not found in an interval, None is placed in the list
    instead of a record.
    
    '''
    data = []
    end = start + (interval * periods)
    curr = (start + interval) - datetime.timedelta(seconds=1)
    if len(qs):
        rec = qs[0]
        rec_class = rec.__class__
    else:
        rec = None
    while periods:
        if rec and rec.timestamp < curr:
            data.append(rec)
            while rec:
                # skip next records less than curr
                try:
                    rec = rec.get_next_by_timestamp()
                except rec_class.DoesNotExist:
                    rec = None
                else:
                    if rec.timestamp > curr:
                        break
        else:
            data.append(None)
        curr += interval
        periods -= 1
    return data

def hourly_data(qs, start):
    # normalize the starting date to midnight
    start.replace(hour=0,minute=0,second=0,microsecond=0)
    return periodic_records(qs, start, datetime.timedelta(hours=1), 24)

def halfhour_data(qs, start):
    # normalize the starting date to midnight
    start.replace(hour=0,minute=0,second=0,microsecond=0)
    return periodic_records(qs, start, datetime.timedelta(minutes=30), 24*2)
    
def ten_minute_data(qs, start):
    # normalize the starting date to midnight
    start.replace(hour=0,minute=0,second=0,microsecond=0)
    return periodic_records(qs, start, datetime.timedelta(minutes=10), 24*6)

def flex_floor(vals, prev):
    vlist = [i for i in vals if i is not None]
    if not vlist:
        return prev
    else:
        if type(vlist[0]) == int:
            return int_floor(vals, prev)
        else:
            return float_floor(vals, prev)

def flex_ceil(vals, prev):
    vlist = [i for i in vals if i is not None]
    if not vlist:
        return prev
    else:
        if type(vlist[0]) == int:
            return int_ceil(vals, prev)
        else:
            return float_ceil(vals, prev)
    
def int_floor(vals, prev):
    '''
    Returns the floor of vals and prev.
    
    '''
    vlist = [i for i in vals if i is not None]
    vlist.append(prev)
    return int(math.floor(float(min(vlist))/10.0)*10)   # round down to nearest ten
    
def int_ceil(vals, prev):
    top = max(max(vals), prev)
    return int(math.ceil(float(top)/10.0)*10)    # round up to nearest ten

def float_floor(vals, prev):
    '''
    Returns the floor of vals and prev.
    
    '''
    vlist = [i for i in vals if i is not None]
    vlist.append(prev)
    return math.floor(float(min(vlist))*10.0)/10.0  # round down to nearest tenth

def float_ceil(vals, prev):
    top = max(max(vals), prev)
    return math.ceil(float(top)*10.0)/10.0  # round up to nearest tenth
