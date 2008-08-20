from django.db import models
from django.contrib import admin
from datetime import datetime


class Foodstuff(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField()
    
    def __str__(self):
        return self.title
    
    def permalink(self):
        return "/food/%s/" % self.slug
    
    class Meta:
        ordering = ['title']


class FoodstuffAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    

class Attribute(models.Model):
    title = models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']


class Category(models.Model):
    title = models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']

    
class Recipe(models.Model):
    title = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField()
    pub_date = models.DateField('date published', null=True, default=datetime.now)
    directions = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    teaser = models.CharField(max_length=100, blank=True, null=True)
    attributes = models.ManyToManyField(Attribute)
    categories = models.ManyToManyField(Category)
    CLASS_CHOICES = (
        ('D', 'Drink'),
        ('E', 'Eat'),
        ('I', 'Ingredient'),
    )
    rclass = models.CharField(max_length=1, choices=CLASS_CHOICES, default='D', blank=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']


class RecipeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'teaser', 'attributes', 'categories', 'rclass', 'pub_date')}),
        ('directions & description', {'fields' : ('directions', 'description'),'classes': ('collapse',)}),
    )
    list_filter = ['rclass']
    
        
class Ingredient(models.Model):
    foodstuff = models.ForeignKey(Foodstuff, core=True, related_name="ingredients")
    recipe = models.ForeignKey(Recipe, edit_inline=models.TABULAR, num_in_admin=5, related_name="ingredients")
    quantity = models.CharField(max_length=20, blank=True, null=True)
    modifier = models.CharField(max_length=50, blank=True, null=True)
    rank = models.IntegerField()
    
    def __str__(self):
        return self.foodstuff.title
    
    class Meta:
        ordering = ['rank']
        verbose_name = "recipe ingredient"
        verbose_name_plural = "recipe_ingredients"


class Link(models.Model):
    title = models.CharField(max_length=50, unique=True)
    url = models.CharField(max_length=250)
    rank = models.IntegerField()
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['rank']
