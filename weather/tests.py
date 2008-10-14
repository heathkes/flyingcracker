#!/usr/bin/env python
from django.test import TestCase
from fc3.weather.utils import *

class PeriodicRecordsTestCase(TestCase):
    fixtures = ['fc3',]
    
    def setUp(self):
        self.start = get_today_timestamp(None)
        self.qs = get_weather_for_date(self.start)
        
    def testPeriodicRecords2Hours(self):
        interval = datetime.timedelta(hours=2)
        periods = 12
        d = periodic_records(self.qs, self.start, interval, periods)
        print interval,periods
        print d
        
    def testPeriodicRecords10Minutes(self):
        interval = datetime.timedelta(minutes=10)
        periods = 24 * 6
        d = periodic_records(self.qs, self.start, interval, periods)
        print interval,periods
        print d