from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from fc3.cam.models import Cam, Category
from fc3 import settings
from fc3.json import JsonResponse

CAM_CATEGORY = "cam_category"
CAM_ID = "cam_id"

def cam_view(request):
    cat_list = Category.objects.all()
    
    # check browser for category cookie
    category_id = request.COOKIES.get(CAM_CATEGORY, None)
    cam_id = request.COOKIES.get(CAM_ID, None)
    
    cam_list, image, category = get_cam_list(category_id, cam_id)

    c = RequestContext(request, {
                'catlist': cat_list,
                'category': category,
                'camlist': cam_list,
                'image': image,
            })
    
    
    #
    # This should determine if we are coming from iPhone HOME (inserting an HTML snippet)
    # or coming from a direct request with no preloaded "stuff".
    #
    #response = render_to_response('cam/iphone/cam-iui.html', c)
    response = render_to_response('cam/iphone/cam-iui.html', c)
    
    
    return response

def cam_list(request):
    # get a list of webcam images associated with a Category
    
    xhr = request.GET.has_key('xhr')
    if xhr:
        cat_id = request.POST.get('cat', None)
        if cat_id:
            try:
                category = Category.objects.get(id=cat_id)
            except Category.DoesNotExist:
                cam_list = Cam.objects.all()
            else:
                if category.title == "All Categories":
                    cam_list = Cam.objects.all()
                else:
                    cam_list = Cam.objects.belongs_to_category(cat_id)
        else:
            cam_list = Cam.objects.all()
            
        response_dict = {}
        index = 0
        obj_dict = {}
        for obj in cam_list:
            obj_dict[index] = dict({'id': obj.id, 'title': obj.title})
            index = index + 1
            
        obj_dict['length'] = index
        obj_dict['category'] = cat_id
        response_dict['images'] = obj_dict
        return JsonResponse(response_dict)

def cam_image(request):
    try:
        id = request.POST.get('id')
        image = Cam.objects.get(id=id)
    except Cam.DoesNotExist:
        image = None
        valid = False
    else:
        # set cookie for default image?
        valid = True
    return JsonResponse({'image': image, 'valid': valid})    
    
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

def get_cam_list(cat_id, cam_id=None):
    '''
    Returns a list of images, a "default" image, and the category these images are in.
    '''
    # Set the image first
    if cam_id:
        try:
            image = Cam.objects.get(id=cam_id)
        except Cam.DoesNotExist:
            image = None
    else:
        image = None
        
    if cat_id:
        try:
            category = Category.objects.get(id=cat_id)
        except Category.DoesNotExist:
            cam_list = Cam.objects.all()
            category = get_default_category()
        else:
            if category.title == "All Categories":
                cam_list = Cam.objects.all()
            else:
                cam_list = Cam.objects.filter(category=category)
                # if we don't already have an image,
                # or the image doesn't appear in the specified category
                # set the image to the first one in the category
                if not image or image not in cam_list:
                    image = cam_list[0]
    else:
        cam_list = Cam.objects.all()
        category = get_default_category()
        
    if not image:
        image = get_default_image()
        
    return cam_list, image, category

def get_default_image():
    try:
        image = Cam.objects.get(title__contains="Whetstone")
    except Cam.DoesNotExist:
        image = None
    return image

def get_default_category():
    return Category.objects.get(title="All Categories")
