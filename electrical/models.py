from django.db import models

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255, help_text="Project name")
    sld_file = models.FileField(upload_to='slds/', null=True, blank=True, help_text="Uploaded SLD file")
    phase = models.CharField(max_length=50, choices=[('single', 'Single Phase'), ('three', 'Three Phase')], default='single')
    load_type = models.CharField(max_length=50, choices=[('inductive', 'Inductive'), ('capacitive', 'Capacitive')], default='inductive')
    ampere = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Project {self.id} - {self.name} ({self.phase}, {self.load_type})"


class Panel(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='panels')
    name = models.CharField(max_length=255, help_text="Panel name (e.g., Main Panel, Sub Panel)")
    size = models.CharField(max_length=50, help_text="Panel size (e.g., 400mm x 600mm)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price for this panel")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.size})"


class Component(models.Model):
    PANEL_COMPONENT_TYPES = [
        ('breaker', 'Breaker'),
        ('contactor', 'Contactor'),
        ('meter', 'Meter'),
        ('capacitor', 'Power Factor Capacitor'),
        ('push_button', 'Push Button'),
        ('indicator', 'Indication Light'),
        ('fan', 'Fan'),
        ('cam_switch', 'Cam Switch'),
        ('other', 'Other'),
    ]

    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, related_name='components')
    name = models.CharField(max_length=255, help_text="Component name (e.g., 3P Breaker, Contactor)")
    type = models.CharField(max_length=50, choices=PANEL_COMPONENT_TYPES, help_text="Component type")
    quantity = models.PositiveIntegerField(default=1, help_text="Number of components used")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit of this component")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price for the component")
    specifications = models.JSONField(null=True, blank=True, help_text="Additional specs (e.g., amperage, voltage)")

    def __str__(self):
        return f"{self.name} ({self.type})"


class Pricing(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='pricing')
    total_panels_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total price for panels")
    total_components_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total price for components")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Overall project price")

    def __str__(self):
        return f"Pricing for {self.project.name}"

# Create your models here.
