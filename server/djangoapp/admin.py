from django.contrib import admin
from .models import CarMake, CarModel, Dealership, Review

admin.site.register(CarMake)
admin.site.register(CarModel)
admin.site.register(Dealership)
admin.site.register(Review)