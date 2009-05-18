from BeautifulSoup import BeautifulStoneSoup, Tag
from datetime import datetime

def convert():
    xml = file('fantasy.xml').read()
    soup = BeautifulStoneSoup(xml)
    events = soup.findAll('object', model='fantasy.event')
    changes = 0
    for e in events:
        date = e.find('field', attrs={"name" : "date"})
        start_date = Tag(soup, 'field', [('type', 'DateField'), ('name', 'start_date')])
        start_date.insert(0, date.contents[0])
        date.replaceWith(start_date)
        
        start_time = e.find('field', attrs={"name" : "start_time"})
        date_string = ' '.join([start_date.contents[0], start_time.contents[0]])
        guess_deadline = Tag(soup, 'field', [('type', 'DateTimeField'), ('name', 'guess_deadline')])
        guess_deadline.insert(0, date_string)
        e.insert(0, guess_deadline)
        changes += 1
    file('fantasy2.xml', 'w').write(str(soup))
    print 'Made %d changes' % changes

if __name__ == '__main__':
    convert()
    