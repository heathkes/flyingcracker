from fc3.cam.models import Cam, Category
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

CAM_CATEGORY = "cam_category"

def camview(request, id=None):
    cat_list = Category.objects.all()
    
    cat_id = request.GET.get('cat')
    if cat_id:
        cam_list, image, category = get_cam_list(cat_id)
    else:
        if id is None:
            image = Cam.objects.get(title__contains="Whetstone")
        else:
            image = get_object_or_404(Cam, id=id)
            
        # check browser for category cookie
        cat_id = request.COOKIES.get(CAM_CATEGORY)
        cam_list, junk, category = get_cam_list(cat_id)

    c = RequestContext(request, {
                'catlist': cat_list,
                'category': category,
                'camlist': cam_list,
                'image': image,
            })
        
    response = render_to_response('cam/view.html', c)
    if cat_id:
        set_cookie(response, CAM_CATEGORY, cat_id)
    return response

def get_cam_list(cat_id):
    if cat_id:
        try:
            category = Category.objects.get(id=cat_id)
            if category.title == "All Categories":
                cam_list = Cam.objects.all()
                image = Cam.objects.get(title="Whetstone")
            else:
                cam_list = Cam.objects.filter(category=category)
                image = cam_list[0]
        except:
            cam_list = Cam.objects.all()
            image = Cam.objects.get(title="Whetstone")
            category = Category.objects.get(title="All Categories")
    else:
        cam_list = Cam.objects.all()
        image = Cam.objects.get(title="Whetstone")
        category = Category.objects.get(title="All Categories")
    return cam_list, image, category

    
from django.conf import settings
import datetime

def set_cookie(response, key, value, expire=None):
    if expire is None:
        max_age = 365*24*60*60  #one year
    else:
        max_age = expire
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, 
        domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
    
