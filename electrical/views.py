from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Panel, Component
from .serializers import ProjectSerializer
from .utils import process_project_data
from rest_framework.permissions import IsAuthenticated

class ProjectCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
#            default_user = User.objects.first()
            project = serializer.save(user=request.user)
            process_project_data(project)  # Process the project data
            return Response({'id': project.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectResultsView(APIView):
    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
            results = {
                'panels': [
                    {
                        'id': panel.id,
                        'name': panel.name,
                        'size': panel.size,
                        'price': panel.price,
                    }
                    for panel in project.panels.all()
                ],
                'components': [
                    {
                        'id': component.id,
                        'name': component.name,
                        'type': component.type,
                        'quantity': component.quantity,
                        'total_price': component.total_price,
                    }
                    for panel in project.panels.all()
                    for component in panel.components.all()
                ],
                'total_price': sum(panel.price for panel in project.panels.all()),
            }
            return Response(results, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
