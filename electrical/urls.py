from django.urls import path
from .views import ProjectCreateView, ProjectResultsView

urlpatterns = [
    path('projects/', ProjectCreateView.as_view(), name='create-project'),
    path('projects/<int:project_id>/results/', ProjectResultsView.as_view(), name='project-results'),
]
