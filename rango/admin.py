from django.contrib import admin
from rango.models import Category, Page

class PageAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'url')  # Order matches your screenshot

admin.site.register(Category)
admin.site.register(Page, PageAdmin)