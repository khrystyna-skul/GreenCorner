from django.contrib import admin
from .models import Plant, Family, Nursery, PlantType

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'difficulty', 'pet_safe')
    search_fields = ('name', 'latin_name')

admin.site.register(Family)
admin.site.register(Nursery)
admin.site.register(PlantType)