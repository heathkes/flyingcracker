
import datetime
from fc3.weather import utils
import fc3.gchart as gchart
from fc3.settings import CHART_ROOT

def create_iphone_charts(date, date_wx, yesterday, yesterday_wx, year_ago, year_ago_wx):
    print 'calculating halfhour weather...'
    date_halfhour_wx = gchart.halfhour_data(date_wx, date)
    print str(date) + ' done'
    yesterday_halfhour_wx = gchart.halfhour_data(yesterday_wx, yesterday)
    print str(yesterday) + ' done'
    year_ago_halfhour_wx = gchart.halfhour_data(year_ago_wx, year_ago)
    print str(year_ago) + ' done'

    # Temperature Charts
    
    # Today, yesterday, year ago
    qs_list = []
    qs_list.append(date_halfhour_wx)
    qs_list.append(yesterday_halfhour_wx)
    qs_list.append(year_ago_halfhour_wx)
    t_chart = utils.day_temp_charts(qs_list, gchart.day_chart_iphone, 260, 100, ['0000FF', '87CEEB', 'BEBEBE'])
    # retrieve and save these charts
    for unit in utils.temp_units:
        filename = utils.temp_chart_filename(unit, date, utils.CHART_TYPE_TDY, 'small')
        print 'downloading ' + filename + '...'
        t_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'

    # Today, year ago
    qs_list = []
    qs_list.append(date_halfhour_wx)
    qs_list.append(year_ago_halfhour_wx)
    t_chart = utils.day_temp_charts(qs_list, gchart.day_chart_iphone, 260, 100, ['0000FF', 'BEBEBE'])
    # retrieve and save these charts
    for unit in utils.temp_units:
        filename = utils.temp_chart_filename(unit, date, utils.CHART_TYPE_TY, 'small')
        print 'downloading ' + filename + '...'
        t_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'


    # Today, yesterday
    qs_list = []
    qs_list.append(date_halfhour_wx)
    qs_list.append(yesterday_halfhour_wx)
    t_chart = utils.day_temp_charts(qs_list, gchart.day_chart_iphone, 260, 100, ['0000FF', '87CEEB'])
    # retrieve and save these charts
    for unit in utils.temp_units:
        filename = utils.temp_chart_filename(unit, date, utils.CHART_TYPE_TD, 'small')
        print 'downloading ' + filename + '...'
        t_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'


    # Today
    qs_list = []
    qs_list.append(date_halfhour_wx)
    t_chart = utils.day_temp_charts(qs_list, gchart.day_chart_iphone, 260, 100, ['0000FF'])
    # retrieve and save these charts
    for unit in utils.temp_units:
        filename = utils.temp_chart_filename(unit, date, utils.CHART_TYPE_T, 'small')
        print 'downloading ' + filename + '...'
        t_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'

    # Barometric Pressure Charts
    
    # Today
    qs_list = []
    qs_list.append(date_halfhour_wx)
    b_chart = utils.day_baro_charts(qs_list, gchart.day_chart_iphone, 292, 120, ['FFCC99'])
    # retrieve and save these charts
    for unit in utils.baro_units:
        filename = utils.baro_chart_filename(unit, date, utils.CHART_TYPE_T, 'small')
        print 'downloading ' + filename + '...'
        b_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'
    
def create_normal_charts(date, date_wx, yesterday, yesterday_wx, year_ago, year_ago_wx):
    date_halfhour_wx = gchart.halfhour_data(date_wx, date)
    yesterday_halfhour_wx = gchart.halfhour_data(yesterday_wx, yesterday)
    year_ago_halfhour_wx = gchart.halfhour_data(year_ago_wx, year_ago)

    # Temperature Charts
    
    # Today, yesterday, year ago
    qs_list = []
    qs_list.append(date_halfhour_wx)
    qs_list.append(yesterday_halfhour_wx)
    qs_list.append(year_ago_halfhour_wx)
    t_chart = utils.day_temp_charts(qs_list, gchart.day_chart_normal, 360, 160, ['0000FF', '87CEEB', 'BEBEBE'])
    # retrieve and save these charts
    for unit in utils.temp_units:
        filename = utils.temp_chart_filename(unit, date, utils.CHART_TYPE_TDY, '')
        print 'downloading ' + filename + '...'
        t_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'

    # Today, year ago
    qs_list = []
    qs_list.append(date_halfhour_wx)
    qs_list.append(year_ago_halfhour_wx)
    t_chart = utils.day_temp_charts(qs_list, gchart.day_chart_normal, 360, 160, ['0000FF', 'BEBEBE'])
    # retrieve and save these charts
    for unit in utils.temp_units:
        filename = utils.temp_chart_filename(unit, date, utils.CHART_TYPE_TY, '')
        print 'downloading ' + filename + '...'
        t_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'


    # Today, yesterday
    qs_list = []
    qs_list.append(date_halfhour_wx)
    qs_list.append(yesterday_halfhour_wx)
    t_chart = utils.day_temp_charts(qs_list, gchart.day_chart_normal, 360, 160, ['0000FF', '87CEEB'])
    # retrieve and save these charts
    for unit in utils.temp_units:
        filename = utils.temp_chart_filename(unit, date, utils.CHART_TYPE_TD, '')
        print 'downloading ' + filename + '...'
        t_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'


    # Today
    qs_list = []
    qs_list.append(date_halfhour_wx)
    t_chart = utils.day_temp_charts(qs_list, gchart.day_chart_normal, 360, 160, ['0000FF'])
    # retrieve and save these charts
    for unit in utils.temp_units:
        filename = utils.temp_chart_filename(unit, date, utils.CHART_TYPE_T, '')
        print 'downloading ' + filename + '...'
        t_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'

    # Barometric Pressure Charts
    
    # Today
    qs_list = []
    qs_list.append(date_halfhour_wx)
    b_chart = utils.day_baro_charts(qs_list, gchart.day_chart_normal, 360, 160, ['FFCC99'])
    # retrieve and save these charts
    for unit in utils.baro_units:
        filename = utils.baro_chart_filename(unit, date, utils.CHART_TYPE_T, '')
        print 'downloading ' + filename + '...'
        b_chart[unit].download(CHART_ROOT+'weather/'+filename)
        print 'done.'
    
def main():
    date = datetime.datetime.today()
    date.replace(hour=0,minute=0,second=0,microsecond=0)
    date_wx = utils.weather_on_date(date)
    
    one_day = datetime.timedelta(days=1)
    yesterday = date - one_day
    yesterday_wx = utils.weather_on_date(yesterday)
    
    one_year = datetime.timedelta(days=365) # don't worry about leap years
    year_ago = date - one_year
    year_ago_wx = utils.weather_on_date(year_ago)
    
    create_iphone_charts(date, date_wx, yesterday, yesterday_wx, year_ago, year_ago_wx)
    create_normal_charts(date, date_wx, yesterday, yesterday_wx, year_ago, year_ago_wx)
    
if __name__=='__main__':
    main()