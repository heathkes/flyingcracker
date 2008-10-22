
class Forecast(object):
    
    def __init__(self):
        self.pubdate = None
        self.area = None
        self.warning = None
        self.sections = []
        self.reported_by = None
        self.timestamp = None
        self.stale = False
        
    def add_section(self, title, body):
        self.sections.append({'title': title, 'body': body})
        
    def __repr__(self):
        s = ''
        if self.pubdate:
            s += "Forecast pubdate: " + self.pubdate + "\n"
        if self.timestamp:
            s += "Forecast timestamp: " + self.timestamp.strftime("%H:%M %Z %a %b %d, %Y") + "\n"
        if self.area:
            s += "Forecast Area: " + self.area + "\n"
        if self.warning:
            s += "Warning: " + self.warning + "\n"
        for sec in self.sections:
            s += sec['title'] + ": " + sec['body'] + "\n"
        if self.reported_by:
            s += "Reported by: " + self.reported_by + "\n"
        return s

