from django.contrib import admin

# Register your models here.
from .models import ConfigimpactTour, ConfigweightTour

admin.site.register(ConfigimpactTour)
admin.site.register(ConfigweightTour)