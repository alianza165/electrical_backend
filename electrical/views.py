from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Project, Panel, Component
from .serializers import ProjectSerializer
import pytesseract
from PIL import Image
import PyPDF2
import os

class ProjectCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        sld_file = request.FILES.get('sld_file')

        if not sld_file:
            return Response({'error': 'No SLD file provided'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            # Save the project
            project = serializer.save(user=request.user)

            try:
                # Process the SLD file and populate panels and components
                process_sld_file(sld_file, project)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


### **Helper Function to Process SLD File**

def process_sld_file(sld_file, project):
    try:
        file_name, file_extension = os.path.splitext(sld_file.name)

        if file_extension.lower() in ['.png', '.jpg', '.jpeg']:
            image = Image.open(sld_file)
            text = pytesseract.image_to_string(image)
            parse_and_populate_project_data(text, project)

        elif file_extension.lower() == '.pdf':
            pdf_reader = PyPDF2.PdfReader(sld_file)
            text = "".join([page.extract_text() for page in pdf_reader.pages])
            parse_and_populate_project_data(text, project)

        else:
            raise ValueError('Unsupported file type. Only PNG, JPG, and PDF files are supported.')

    except Exception as e:
        print(f"Error processing SLD file: {e}")
        raise


def parse_and_populate_project_data(text, project):
    # Mock parsing logic (Replace with actual parsing logic based on your SLD structure)
    panels = [
        {"name": "Panel A", "size": "Medium", "price": 500},
        {"name": "Panel B", "size": "Large", "price": 1000},
    ]

    components = [
        {"name": "MCB 10A SP 6KA", "type": "Breaker", "quantity": 10, "unit_price": 50},
        {"name": "ELCB 63A", "type": "Protector", "quantity": 2, "unit_price": 200},
    ]

    # Populate panels and components in the database
    for panel_data in panels:
        panel = Panel.objects.create(
            project=project,
            name=panel_data['name'],
            size=panel_data['size'],
            price=panel_data['price'],
        )

        for component_data in components:
            Component.objects.create(
                panel=panel,
                name=component_data['name'],
                type=component_data['type'],
                quantity=component_data['quantity'],
                unit_price=component_data['unit_price'],  # Ensure unit_price is provided
                total_price=component_data['quantity'] * component_data['unit_price'],  # Calculate total price
            )
