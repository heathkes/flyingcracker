#!/usr/bin/env python
from django.contrib import admin
import fc3.food.models as food

admin.site.register(food.Foodstuff, food.FoodstuffAdmin)
admin.site.register(food.Attribute)
admin.site.register(food.Category)
admin.site.register(food.Recipe, food.RecipeAdmin)
admin.site.register(food.Ingredient)
admin.site.register(food.Link)
