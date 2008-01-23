from fc3.cam.models import Cam, Category
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from fc3.json import JsonResponse

CAM_CATEGORY = "cam_category"

def cam_list(request):
    # get a list of webcam images associated with this Category
    cat_id = request.POST.get('cat')
    if cat_id:
        category = Category.objects.get(id=cat_id)
        if category.title == "All Categories":
            cam_list = Cam.objects.all()
        else:
            cam_list = Cam.objects.belongs_to_category(cat_id)
            
        response_dict = {}
        index = 0
        obj_dict = {}
        for obj in cam_list:
            obj_dict[index] = dict({'id': obj.id, 'title': obj.title})
            index = index + 1
            
        obj_dict['length'] = index
        obj_dict['category'] = cat_id
        response_dict['images'] = obj_dict
        
        xhr = request.GET.has_key('xhr')
        if xhr:
            return JsonResponse(response_dict)

def cam_view(request, id=None):
    cat_list = Category.objects.all()
    
    # check browser for category cookie
    cat_id = request.COOKIES.get(CAM_CATEGORY)
    cam_list, image, category = get_cam_list(cat_id)

    if id:
        image = get_object_or_404(Cam, id=id)
            
    c = RequestContext(request, {
                'catlist': cat_list,
                'category': category,
                'camlist': cam_list,
                'image': image,
            })
        
    response = render_to_response('cam/cam_small.html', c)
    if cat_id:
        set_cookie(response, CAM_CATEGORY, cat_id)
    return response

def cam_suggestion(request):
    url = request.POST.get('url')
    description = request.POST.get('description')
    
    from django.core.mail import send_mail
    
    subject = "webcam suggestion"
    message = render_to_string('suggestion/suggestion_email.txt',
                               { 'cam_url': url,
                                 'cam_description': description })
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ["webcam@flyingcracker.com"])
    return JsonResponse({'success': True})

def get_cam_list(cat_id):
    '''
    Returns a list of images, a "default" image, and the category these images are in.
    '''
    if cat_id:
        try:
            category = Category.objects.get(id=cat_id)
            if category.title == "All Categories":
                cam_list = Cam.objects.all()
                image = get_default_image()
            else:
                cam_list = Cam.objects.filter(category=category)
                image = cam_list[0]
        except:
            cam_list = Cam.objects.all()
            image = get_default_image()
            category = get_default_category()
    else:
        cam_list = Cam.objects.all()
        image = get_default_image()
        category = get_default_category()
    return cam_list, image, category

def get_default_image():
    return Cam.objects.get(title__contains="Whetstone")
def get_default_category():
    return Category.objects.get(title="All Categories")
    
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
    
