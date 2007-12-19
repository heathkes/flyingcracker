from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=30)
    
    def __str__(self):
        return self.title
    
    class Admin:
        pass
    
class CamManager(models.Manager):
    def belongs_to_category(self, cat=None):
        '''
        Returns a queryset of all Cams associated with specified Category.
        '''
        qs = super(type(self), self).get_query_set()
        if cat:
            qs = qs.filter(category=cat)
            return qs
        else:
            return qs
    
class Cam(models.Model):
    title = models.CharField(max_length=100)
    state = models.USStateField(default="CO")
    url = models.URLField()
    category = models.ForeignKey(Category)
    objects = CamManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        
    class Admin:
        # Admin options go here
        pass
