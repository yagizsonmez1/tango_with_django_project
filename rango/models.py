from django.db import models
from django.template.defaultfilters import slugify

from tango_with_django_project.rango import forms

class Category(models.Model):
    NAME_MAX_LENGTH = 128  # Define as a class attribute
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    name = models.CharField(max_length=128, unique=True) 
    name = forms.CharField(max_length=Category.NAME_MAX_LENGTH, help_text="Please enter the category name.")
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name) 
        super(Category, self).save(*args, **kwargs)


    class Meta:
        verbose_name_plural = 'Categories'


    def __str__(self): 
        return self.name

class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE) 
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __str__(self): 
        return self.title

