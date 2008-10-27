#!/usr/bin/env python
from xml.etree.ElementTree import XML
from xml.parsers.expat import ExpatError
from urllib import urlopen
from dateutil import parser as dateutilparser
from fc3.weatherstation.tz import USTimeZone
from forecast import Forecast


class CBTVForecast(Forecast):

    def set_timestamp(self, pubdate = None):
        if pubdate == None:
            pubdate = self.pubdate
        if pubdate:
            self.timestamp = dateutilparser.parse(pubdate)
            mountain_tz = USTimeZone(-7, "Mountain", "MST", "MDT")
            self.timestamp = self.timestamp.astimezone(mountain_tz)
        
        
def get_CBTV_forecast():
    '''
    Obtain latest CBTV RSS feed
    Parse into the pieces we want (synopsis, today, tonight, tomorrow)
    Format nicely into parts
    '''
    url = 'http://www.cbtv.tv/RSS/CrestedButteCurrentWeatherReport.xml'
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
    synopsis = item.findtext("description")
    reportedby = item.findtext("dc")

    forecast = CBTVForecast()
    forecast.pubdate = pubdate
    forecast.set_timestamp()
    forecast.add_section('Synopsis', synopsis.strip())
    if reportedby:
        forecast.reported_by = reportedby.strip()
                         
    return forecast

        
def test():
    forecast = get_CBTV_forecast()
    print repr(forecast)
    
if __name__ == '__main__':
    test()

