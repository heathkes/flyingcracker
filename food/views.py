# Create your views here.
from fc3.food.models import Recipe
from django.shortcuts import render_to_response, get_object_or_404

def index(request):
    all_recipes = Recipe.objects.all().order_by('title')
    return render_to_response('food/index.html', {'all_recipes' : all_recipes})
    
def detail(request, recipe_slug):
    r = get_object_or_404(Recipe, slug=recipe_slug)
    return render_to_response('food/detail.html', {'recipe' : r})    