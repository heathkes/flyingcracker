from xml.etree.ElementTree import XML
from xml.parsers.expat import ExpatError
from urllib import urlopen
from dateutil import parser as dateutilparser
#from fc3.weatherstation.tz import USTimeZone
from forecast import Forecast


class CBACForecast(Forecast):

    def set_timestamp(self, pubdate = None):
        if pubdate == None:
            pubdate = self.pubdate
        if pubdate:
            self.timestamp = dateutilparser.parse(pubdate)
            mountain_tz = USTimeZone(-7, "Mountain", "MST", "MDT")
            self.timestamp = self.timestamp.astimezone(mountain_tz)
        
        
def get_CBAC_forecast():
    '''
    Obtain latest CBAC RSS feed
    Parse into the pieces we want (synopsis, today, tonight, tomorrow)
    Format nicely into parts
    '''
    url = 'http://cbavalanchecenter.org/rss/'
    try:
        xml_text = urlopen(url).read()
    except IOError:
        return None
    
    try:
        xml = XML(xml_text)
    except ExpatError, info:
        return None;    # fail silently
    
    rss = xml
    channel = rss.find('channel')
    item = channel.find('item')
    
    # Get the data we want
    pubdate = item.findtext('pubdate')
    
    report_el = item.find('report')
    synopsis = report_el.findtext("weathersynopsis")
    reportedby = report_el.findtext("reportedby")
    
    forecast_el = report_el.find('forecast')
    today = forecast_el.findtext('today')
    tonight = forecast_el.findtext('tonight')
    tomorrow = forecast_el.findtext('tomorrow')

    forecast = CBACForecast()
    forecast.pubdate = pubdate
    forecast.set_timestamp()
    forecast.add_section('Synopsis', synopsis.strip())
    forecast.add_section('Today', today.strip())
    forecast.add_section('Tonight', tonight.strip())
    forecast.add_section('Tomorrow', tomorrow.strip())
    forecast.reported_by = reportedby.strip()
                         
    return forecast

        
def test():
    forecast = get_CBAC_forecast()
    print repr(forecast)
    
if __name__ == '__main__':
    test()
