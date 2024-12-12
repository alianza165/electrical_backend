from django.contrib import admin
from .models import Project, Panel, Component, Pricing

admin.site.register(Project)
admin.site.register(Panel)
admin.site.register(Component)
admin.site.register(Pricing)

# Register your models here.
