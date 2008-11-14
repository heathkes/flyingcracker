from django.template import RequestContext
from fc3.grill.models import Food, Doneness, Grilling, Hardware
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse

def grill(request):
    '''
    
    
    Passes to the main template:
    `food_list` - a list of all Food items
    `food` - currently selected Food object
    `doneness` - currently selected Doneness object
    `hardware` - currently selected Hardware object
    `less_done` - Doneness id or None
    `more_done` - Doneness id or None
    `grill_items` - list of dicts containing a Cut, Method, and Grilling.details
    '''
    food_list = Food.objects.all()

    if request.GET.has_key('snippet'):
        # parameters expected
        food_id = request.GET.get('food', 1)
        doneness_id = request.GET.get('doneness', 2)
        hardware_id = request.GET.get('hardware', 1)
    else:
        # no parameters expected, but check for cookies
        food_id = 1
        doneness_id = 2
        hardware_id = 1

    food = Food.objects.get(id=food_id)
    doneness = Doneness.objects.get(id=doneness_id)
    hardware = Hardware.objects.get(id=hardware_id)
    less_done = doneness.less()
    more_done = doneness.more()
    grill_items = Grilling.objects.filter(food=food, doneness=doneness, hardware=hardware)
    
    alternatives = []
    if not grill_items:
        qs = Doneness.objects.filter(grilling__food=food, grilling__hardware=hardware).distinct()
        for obj in qs:
            d = {}
            d['link'] = reverse('grill')+"?food=%d&doneness=%d&hardware=%d" % (food.id, obj.id, hardware.id)
            d['title'] = str(food) + ' - ' + str(obj)
            alternatives.append(d)
            
    c = RequestContext(request, {'food_list': food_list,
                                 'food': food,
                                 'doneness': doneness,
                                 'hardware': hardware,
                                 'less_done': less_done,
                                 'more_done': more_done,
                                 'grill_items': grill_items,
                                 'alternatives': alternatives,
                                })
        
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        if request.GET.has_key('snippet'):
            return render_to_response('grill/iphone/snippet.html', c)
        elif request.GET.has_key('iui'):
            return render_to_response('grill/iphone/iui.html', c)
        else:
            return render_to_response('grill/iphone/grill.html', c)
    else:
        # BUGBUG 2008-11-13 - Should be using "normal" browser templates,
        #        if they are different from the iPhone templates.
        if request.GET.has_key('snippet'):
            return render_to_response('grill/iphone/snippet.html', c)
        elif request.GET.has_key('iui'):
            return render_to_response('grill/iphone/iui.html', c)
        else:
            return render_to_response('grill/iphone/grill.html', c)
    
def doneness_detail(request, slug):
    doneness = Doneness.objects.get(slug=slug)
    c = RequestContext(request, {'doneness': doneness,
                                })
    return render_to_response('grill/iphone/doneness_detail.html', c)

def doneness_request(request):
    doneness_id = request.GET.get('id', 2)
    doneness = Doneness.objects.get(id=doneness_id)
    less_done = doneness.less()
    more_done = doneness.more()
    c = RequestContext(request, {'doneness': doneness,
                                 'less_done': less_done,
                                 'more_done': more_done,
                                })
    return render_to_response('grill/iphone/doneness.html', c)
