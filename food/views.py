# Create your views here.
from fc3.food.models import Recipe, Foodstuff
from django.shortcuts import render_to_response, get_object_or_404

def index(request):
    all_recipes = Recipe.objects.all().order_by('title')
    return render_to_response('food/index.html', {'all_recipes' : all_recipes})
    
def detail(request, recipe_slug):
    r = get_object_or_404(Recipe, slug=recipe_slug)
    
    # get ingredients for this recipe
    ingredient_list = []
    for i in r.ingredient_set.all().order_by('rank'):
        ingredient_dict = {}
        ingredient_dict['title'] = i.foodstuff.title
        ingredient_dict['slug'] = i.foodstuff.slug
        ingredient_dict['quantity'] = i.quantity
        ingredient_dict['modifier'] = i.modifier
        ingredient_list.append(ingredient_dict)
    
    return render_to_response('food/detail.html', {'recipe' : r, 'ingredients' : ingredient_list})    
    
def foodstuff(request):
    all_foodstuff = Foodstuff.objects.all().order_by('title')
    return render_to_response('food/foodstuff.html', {'all_foodstuff' : all_foodstuff})
    
def foodstuff_detail(request, foodstuff_slug):
    f = get_object_or_404(Foodstuff, slug=foodstuff_slug)
    recipe_list = []
    
    return render_to_response('food/foodstuff_detail.html', {'foodstuff' : f, 'recipes' : recipe_list})
    