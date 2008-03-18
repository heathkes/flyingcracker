from django.shortcuts import render_to_response

def search1(request):
    return render_to_response('frames.html', {})

def search2(request):
    return render_to_response('s2.html', {})

def search3(request):
    return render_to_response('s3.html', {})