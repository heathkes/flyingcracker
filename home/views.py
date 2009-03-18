from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from fc3.home import models
from serviceclient.models import ServiceClient, ServiceClientUserProfile

def home(request):
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        c = RequestContext(request)
        return render_to_response('home/iphone/home.html', c)
    else:
        return HttpResponseRedirect(reverse('fc-weather'))

def about(request):
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        c = RequestContext(request)
        return render_to_response('home/iphone/about.html', c)
    else:
        return HttpResponseRedirect(reverse('fc-weather'))

@login_required
def service_client_set(request, redirect_field_name=REDIRECT_FIELD_NAME):
    if request.user.is_staff:
        qs = ServiceClient.objects.all()
    else:
        qs = ServiceClient.objects.filter(serviceclientuserprofile__user=request.user)
    
    if len(qs) == 1:
        sc = qs[0]
    else:
        sc = qs[0]
        # BUGBUG 2/26/09
        # present a ServiceClient list
    
    '''
    BUGBUG - 2/27/09
    There may not be a SCUP for an is_staff User for the selected ServiceClient!
    
    '''
    scup = ServiceClientUserProfile.objects.get(user=request.user, service_client=sc)
    request.session['scup'] = scup
    
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    return HttpResponseRedirect(redirect_to)
    