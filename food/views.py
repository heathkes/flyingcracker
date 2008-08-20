from django.template import RequestContext
from fc3.food.models import Recipe, Foodstuff, Link
from django.shortcuts import render_to_response, get_object_or_404
from django.template.defaultfilters import random

def recipe_list(request, recipe_type=""):
    all_recipes, all_foodstuff = get_all_lists(recipe_type)
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        c = RequestContext(request, {'recipe_list' : all_recipes,
                                     'foodstuff_list': all_foodstuff,
                                     'recipe_type': recipe_type,
                                    })
        return render_to_response('food/recipe_detail_small.html', c)
    else:
        all_links = Link.objects.all()
        c = RequestContext(request, {'all_recipes' : all_recipes,
                                     'all_links' : all_links,
                                     'recipe_type': recipe_type,
                                    })
        return render_to_response('food/recipe_list.html', c)
    
def recipe_detail(request, slug, recipe_type=""):
    r = get_object_or_404(Recipe, slug=slug)
    
    all_recipes, all_foodstuff = get_all_lists(recipe_type)
        
    # get ingredients for this recipe
    ingredient_list = []
    for i in r.ingredients.all().order_by('rank'):
        ingredient_dict = {}
        ingredient_dict['title'] = i.foodstuff.title
        ingredient_dict['slug'] = i.foodstuff.slug
        ingredient_dict['permalink'] = i.foodstuff.permalink()
        ingredient_dict['quantity'] = i.quantity
        ingredient_dict['modifier'] = i.modifier
        ingredient_list.append(ingredient_dict)

    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        c = RequestContext(request, {'recipe_list' : all_recipes,
                                     'foodstuff_list': all_foodstuff,
                                     'recipe' : r,
                                     'ingredients' : ingredient_list,
                                     'recipe_type': recipe_type,
                                    })
        return render_to_response('food/recipe_detail_small.html', c)
    else:
        all_links = Link.objects.all()
        c = RequestContext(request, {'recipe_type': recipe_type,
                                     'recipe' : r,
                                     'ingredients' : ingredient_list,
                                     'all_links' : all_links,
                                    })
        return render_to_response('food/recipe_detail.html', c)
    
def foodstuff_list(request, recipe_type=""):
    all_recipes, all_foodstuff = get_all_lists(recipe_type)
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        c = RequestContext(request, {'recipe_list' : all_recipes,
                                     'foodstuff_list': all_foodstuff,
                                     'recipe_type': recipe_type,
                                    })
        return render_to_response('food/foodstuff_detail_small.html', c)
    else:
        all_links = Link.objects.all()
        c = RequestContext(request, {'all_foodstuff' : all_foodstuff,
                                     'all_links' : all_links,
                                     'recipe_type': recipe_type,
                                    })
        return render_to_response('food/foodstuff_list.html', c)
    
def foodstuff_detail(request, slug, recipe_type=""):
    f = get_object_or_404(Foodstuff, slug=slug)
    
    all_recipes, all_foodstuff = get_all_lists(recipe_type)
    ingredient_list = f.ingredients.all().order_by('recipe')
    agent = request.META.get('HTTP_USER_AGENT')
    if (agent and agent.find('iPhone') != -1) or request.GET.has_key('iphone'):
        c = RequestContext(request, {'recipe_list': all_recipes,
                                     'foodstuff_list' : all_foodstuff,
                                     'foodstuff' : f,
                                     'ingredients' : ingredient_list,
                                     'recipe_type': recipe_type,
                                    })
        return render_to_response('food/foodstuff_detail_small.html', c)
    else:
        all_links = Link.objects.all()
        c = RequestContext(request, {'foodstuff' : f,
                                     'ingredients' : ingredient_list,
                                     'all_links' : all_links,
                                     'recipe_type': recipe_type,
                                    })
        return render_to_response('food/foodstuff_detail.html', c)
    
def get_all_lists(recipe_type):
    all_recipes = Recipe.objects.filter(rclass=db_recipe_type(recipe_type)).order_by('title')
    all_foodstuffs = Foodstuff.objects.filter(ingredients__recipe__rclass=db_recipe_type(recipe_type)).distinct().order_by('title')
    return all_recipes, all_foodstuffs

def db_recipe_type(recipe_type):
    if recipe_type == "food":
        return "F"
    else:
        return "D"
