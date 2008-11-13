#!/usr/bin/env python
from datetime import *
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from fc3.json import JsonResponse
from fc3.weatherstation.models import Weather
from noaa import get_NOAA_forecast
from cbac import get_CBAC_forecast
from cbtv import get_CBTV_forecast
import fc3.weather.utils as utils
from fc3.weather.models import ChartUrl
from fc3.utils import ElapsedTime

def weather(request):
    et = ElapsedTime()

    # get latest weather reading
    current = Weather.objects.latest('timestamp')
    
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
        
    # set wind background compass and wind speed
    if int(float(current.wind_speed)) < 1:
        wind = 0
        wind_dir = None
    else:
        wind = current.wind_speed
        wind_dir = "wind-%s.png" % utils.wind_dir_to_english(wind)
        wind_dir = wind_dir.lower()
    wind_list = utils.calc_speeds(wind)

    today = utils.get_today_timestamp(request)
    if today.hour < 12:
        morning = True
    else:
        morning = False

    et.mark_time('initial')
    
    cbac_forecast = get_CBAC_forecast()
    noaa_forecast = get_NOAA_forecast('CO', 12)     # Crested Butte area
    cbtv_forecast = get_CBTV_forecast()

    et.mark_time('forecasts')
    
    t_chart = []
    b_chart = []
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        for unit in utils.temp_units:
            t_chart.append(get_chart(utils.get_today(request), ChartUrl.DATA_TEMP, ChartUrl.SIZE_IPHONE, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))
        for unit in utils.baro_units:
            b_chart.append(get_chart(utils.get_today(request), ChartUrl.DATA_PRESS, ChartUrl.SIZE_IPHONE, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))
        
        et.mark_time('charts')
        
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
                'cbtv': cbtv_forecast,
                'unit_state': unit_state,
                'title_state': title_state,
                'elapsed': et.list(),
                })

        if request.GET.has_key('iui'):
            return render_to_response('weather/iphone/weather-iui.html', c)
        else:
            return render_to_response('weather/iphone/weather.html', c)
    else:
        t_chart = get_chart(utils.get_today(request), ChartUrl.DATA_TEMP, ChartUrl.SIZE_NORMAL, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, utils.TEMP_F)
        b_chart = get_chart(utils.get_today(request), ChartUrl.DATA_PRESS, ChartUrl.SIZE_NORMAL, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, utils.PRESS_IN)
        
        et.mark_time('charts')

        trend_list = utils.calc_trend_strings(current.baro_trend)
    
        c = RequestContext(request, {
                'current': current,
                'trend': trend_list[0],
                'wind_dir': wind_dir,
                'wind_speed': wind_list[0],
                'morning': morning,
                'show_titles': show_titles,
                'show_units': show_units,
                'temp_chart': t_chart,
                'baro_chart': b_chart,
                'cbac': cbac_forecast,
                'noaa': noaa_forecast,
                'cbtv': cbtv_forecast,
                'unit_state': unit_state,
                'title_state': title_state,
                'elapsed': et.list(),
                })
        return render_to_response('weather/current.html', c)


def current(request):
    from django.template.defaultfilters import date as date_filter

    xhr = request.GET.has_key('xhr')
    if xhr:
        # get latest weather reading
        current = Weather.objects.latest('timestamp')
        
        timestamp = date_filter(current.timestamp, "H:i \M\T D M j,Y")

        temp_list = utils.calc_temp_strings(current.temp)
        baro_list = utils.calc_baro_strings(current.barometer)
        trend_list = utils.calc_trend_strings(current.baro_trend)
        
        if int(float(current.wind_speed)) < 1:
            wind = 0
            wind_dir = None
        else:
            wind = current.wind_speed
            wind_dir = "wind-%s.png" % utils.wind_dir_to_english(wind)
            wind_dir = wind_dir.lower()
        wind_list = utils.calc_speeds(wind)
        
        temp_unit = request.COOKIES.get("temp_unit")
        if temp_unit is None:
            temp_unit = utils.TEMP_F
            
        baro_unit = request.COOKIES.get("baro_unit")
        if baro_unit is None:
            baro_unit = utils.PRESS_IN
            
        if wind == 0:
            speed_unit = ""
            wind_units = [""]
        else:
            speed_unit = request.COOKIES.get("speed_unit")
            wind_units = utils.speed_units
            if speed_unit is None:
                speed_unit = utils.SPEED_MPH
        
        windchill_list = utils.calc_temp_strings(current.windchill)
        
        today = utils.get_today_timestamp(request)
        if today.hour < 12:
            morning = True
        else:
            morning = False

        t_chart = []
        b_chart = []
        agent = request.META.get('HTTP_USER_AGENT')
        if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
            for unit in utils.temp_units:
                t_chart.append(get_chart(utils.get_today(request), ChartUrl.DATA_TEMP, ChartUrl.SIZE_IPHONE, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))
            for unit in utils.baro_units:
                b_chart.append(get_chart(utils.get_today(request), ChartUrl.DATA_PRESS, ChartUrl.SIZE_IPHONE, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))
        else:
            for unit in utils.temp_units:
                t_chart.append(get_chart(utils.get_today(request), ChartUrl.DATA_TEMP, ChartUrl.SIZE_NORMAL, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))
            for unit in utils.baro_units:
                b_chart.append(get_chart(utils.get_today(request), ChartUrl.DATA_PRESS, ChartUrl.SIZE_NORMAL, ChartUrl.PLOT_TODAY+ChartUrl.PLOT_YESTERDAY+ChartUrl.PLOT_YEAR_AGO, unit))

        response_dict = {}
        response_dict.update({'timestamp': timestamp})
        response_dict.update({'temp_units': utils.temp_units})
        response_dict.update({'baro_units': utils.baro_units})
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
    
    # set unit preference in user profile
    # ...
    
    # return same data, just for grins
    response_dict = {}
    response_dict.update({'type': type})
    response_dict.update({'unit': unit})
    response = JsonResponse(response_dict)
    return response


from fc3.weather.models import ChartUrl

def get_chart(date, data_type, size, plots, unit):
    now = datetime.now()
    try:
        chart = ChartUrl.objects.get(date=date, data_type=data_type, size=size, plots=plots, unit=unit)
    except ChartUrl.DoesNotExist:
        # create url
        chart = ChartUrl(date=date, timestamp=now, data_type=data_type, size=size, plots=plots, unit=unit)
        chart.url = utils.create_chart_url(date, data_type, size, plots, unit)
        try:
            chart.save()
        except ChartUrl.IntegrityError: # someone else got it done first
            pass
    else:
        # recreate url if timestamp is 30 minutes older than now
        if (now - chart.timestamp) > timedelta(minutes=30):
            # re-create url
            chart.url = utils.create_chart_url(date, data_type, size, plots, unit)
            chart.timestamp = now
            chart.save()
    return chart.url

from django import forms
from django.forms import ModelForm


class WeatherForm(ModelForm):
    class Meta:
        model = Weather


class GenerateWeatherForm(WeatherForm):
    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()
    
    def clean(self):
        start = self.cleaned_data.get('start_date')
        end = self.cleaned_data.get('end_date')
        if start and end:
            if end < start:
                raise forms.ValidationError('Start date/time (%s) must be prior to end date/time (%s)' % (str(start), str(end)))
        return self.cleaned_data
            
    class Meta(WeatherForm.Meta):
        exclude = ('station_id', 'timestamp', 'temp_inside', 'rain', 'wind_peak', 'dewpoint', 'windchill')

def generate(request):
    if request.method == 'POST': # If the form has been submitted...
        form = GenerateWeatherForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            cd = form.cleaned_data
            interval = timedelta(minutes=5)
            start = cd['start_date']
            curr = start
            end = cd['end_date']
            inserted = attempts = 0
            et = ElapsedTime()
            while curr <= end:
                obj = Weather(station_id='GENERATED',
                              timestamp=curr,
                              wind_dir=cd['wind_dir'],
                              wind_speed=cd['wind_speed'],
                              wind_peak=0,
                              humidity=cd['humidity'],
                              temp=cd['temp'],
                              rain=0,
                              barometer=cd['barometer'],
                              dewpoint=0,
                              temp_inside=0,
                              baro_trend=cd['baro_trend'],
                              windchill=0)
                try:
                    obj.save()
                except Weather.IntegrityError:
                    pass    # leave the existing record in place
                else:
                    inserted += 1
                curr += interval
                attempts += 1
                
            et.mark_time('insertions')
            c = RequestContext(request, {
                    'elapsed': et.list(),
                    'message': 'Added %d Weather records in %d attempts, from %s to %s.' % (inserted, attempts, str(start), str(end)),
                    })
            return render_to_response('weather/after_action.html', c)
    else:
        form = GenerateWeatherForm() # An unbound form

    c = RequestContext(request, {
            'form': form,
        })
    return render_to_response('weather/generate.html', c)

class DeleteWeatherForm(forms.Form):
    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()
    
    def clean(self):
        start = self.cleaned_data.get('start_date')
        end = self.cleaned_data.get('end_date')
        if start and end:
            if end < start:
                raise forms.ValidationError('Start date/time (%s) must be prior to end date/time (%s)' % (str(start), str(end)))
        return self.cleaned_data

def delete(request):
    if request.method == 'POST': # If the form has been submitted...
        form = DeleteWeatherForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            cd = form.cleaned_data
            start = cd['start_date']
            end = cd['end_date']
            records = Weather.objects.filter(timestamp__range=(start, end))
            deleted = attempts = 0
            et = ElapsedTime()
            for obj in records:
                try:
                    obj.delete()
                except:
                    pass
                else:
                    deleted += 1
                attempts += 1
                
            et.mark_time('deletions')
            c = RequestContext(request, {
                    'elapsed': et.list(),
                    'message': 'Deleted %d Weather records in %d attempts, from %s to %s..' % (deleted, attempts, str(start), str(end)),
                    })

            return render_to_response('weather/after_action.html', c)
    else:
        form = DeleteWeatherForm() # An unbound form

    c = RequestContext(request, {
            'form': form,
        })
    return render_to_response('weather/delete.html', c)

def output_data(request):
    import csv
    from dateutil.parser import parse as dateparse
    
    item = request.GET.get('item')
    if item == 'temp':
        attr = item
    elif item == 'pressure':
        attr = 'barometer'
    elif item == 'humidity':
        attr = item
    elif item == 'windchill':
        attr = item
    else:
        return HttpResponse(content='unsupported data item: "%s"' % str(item))
    
    type = request.GET.get('type')
    if type == 'range':
        today_str = date.today().strftime('%Y-%m-%d')
        start_str = request.GET.get('start', today_str)
        end_str = request.GET.get('end', today_str)
        try:
            start = dateparse(start_str)
            end = dateparse(end_str)
        except ValueError:
            return HttpResponse(content='unrecognized date format: start="%s", end="%s". Please use YYYY-MM-DD format.' % (start_str, end_str))
        
        target = date(start.year, start.month, start.day)
        end = date(end.year, end.month, end.day)
        interval = timedelta(days=1)

        if target > end:
            return HttpResponse(content='start (%s) cannot be later than end (%s)' % (str(target), str(end)))
        
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=fc3weatherdata.csv'
        writer = csv.writer(response)
        writer.writerow(['date', 'temp:low', 'temp:high'])
        
        # Get the high and low temp for each date.
        while target <= end:
            qs = Weather.objects.filter(timestamp__year=target.year, timestamp__month=target.month, timestamp__day=target.day)
            vals = [rec.__getattribute__(attr) for rec in qs]
            if vals:
                low = min(vals)
                high = max(vals)
            else:
                low = high = 'N/A'
            writer.writerow([str(target), str(low), str(high)])
            target += interval
        return response
    else:
        return HttpResponse(content='unsupported report type: "%s"' % str(type))