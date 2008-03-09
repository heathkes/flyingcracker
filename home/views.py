from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

def home(request):
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        return render_to_response('home/home.html')
    else:
        return HttpResponseRedirect("/blog/")
