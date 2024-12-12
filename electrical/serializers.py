from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'sld_file', 'phase', 'load_type', 'ampere']
        read_only_fields = ['id']
