#!/usr/bin/env python
from fc3.pygooglechart import XYLineChart, Axis, TextDataWithScaling

DAY_HOUR_DATA = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24)
DAY_EVERY_3HOURS_LABELS = ['', '3a', '6a', '9a', '12', '3p', '6p', '9p', '']
DAY_EVERY_HOUR_LABELS = ['', '1a', '2a', '3a', '4a', '5a', '6a', '7a', '8a', '9a', '10a', '11a', '12',
                         '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', '10p', '11p', '']

def xchart(x_data, x_labels, data_lists, y_floor, y_ceil, width, height, colors):
    '''
    Returns the URL for a chart where all datasets use the same X-axis values.
    Y-axis labels are shown on both sides of the graph.
    
    '''
    x_floor = min((i for i in x_data if i is not None))
    x_ceil = max(x_data)
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
    chart.set_line_style(0, 3)
    return chart.get_url(TextDataWithScaling)