from django.contrib import admin
from rango.models import Category, Page

class PageAdmin(admin.ModelAdmin):
    # Changed order: Title first, then Category, then URL
    list_display = ('title', 'category', 'url')  # 🔄 Order swapped

admin.site.register(Category)
admin.site.register(Page, PageAdmin)