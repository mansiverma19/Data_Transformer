from django.contrib import admin
from .models import Insurer, Category, Month, Products

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('clubbed_name', 'category')

class InsurerAdmin(admin.ModelAdmin):
    list_display = ('insurer', 'name', 'get_clubbedname')

    def get_clubbedname(self, obj):
        return obj.clubbed_name.clubbed_name

admin.site.register(Category, CategoryAdmin)
admin.site.register(Insurer, InsurerAdmin)
admin.site.register(Products)
admin.site.register(Month)
