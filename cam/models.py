from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=30)
    
    def __str__(self):
        return self.title
    
    class Admin:
        pass
    
class Cam(models.Model):
    title = models.CharField(max_length=100)
    state = models.USStateField()
    url = models.URLField()
    category = models.ForeignKey(Category)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        
    class Admin:
        # Admin options go here
        pass
