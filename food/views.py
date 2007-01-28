# Create your views here.
from fc3.food.models import Recipe, Foodstuff, Link
from django.shortcuts import render_to_response, get_object_or_404

def all_recipes(request, recipe_type=""):
    all_recipes = Recipe.objects.filter(rclass=recipe_type).order_by('title')
    all_links = Link.objects.all()
    return render_to_response('food/all_recipes.html', {'all_recipes' : all_recipes, 'all_links' : all_links})
    
def recipe_detail(request, slug, recipe_type=""):
    r = get_object_or_404(Recipe, slug=slug)
    
    # get ingredients for this recipe
    ingredient_list = []
    for i in r.ingredient_set.all().order_by('rank'):
        ingredient_dict = {}
        ingredient_dict['title'] = i.foodstuff.title
        ingredient_dict['slug'] = i.foodstuff.slug
        ingredient_dict['quantity'] = i.quantity
        ingredient_dict['modifier'] = i.modifier
        ingredient_list.append(ingredient_dict)
    
    all_links = Link.objects.all()
    return render_to_response('food/recipe_detail.html', {'recipe' : r, 'ingredients' : ingredient_list, 'all_links' : all_links})
    
def all_foodstuffs(request, recipe_type=""):
    all_foodstuff = Foodstuff.objects.all().order_by('title')
    all_links = Link.objects.all()
    return render_to_response('food/all_foodstuffs.html', {'all_foodstuff' : all_foodstuff, 'all_links' : all_links})
    
def foodstuff_detail(request, slug, recipe_type=""):
    f = get_object_or_404(Foodstuff, slug=slug)
    ingredient_list = f.ingredient_set.all().order_by('recipe')
    all_links = Link.objects.all()
    
    return render_to_response('food/foodstuff_detail.html', {'foodstuff' : f, 'ingredients' : ingredient_list, 'all_links' : all_links})
    