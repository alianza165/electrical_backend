from .models import Panel, Component

def process_project_data(project):
    # Example logic for generating panels and components
    if project.phase == 'single':
        panel_count = 1
        panel_size = '400x600'
    else:
        panel_count = 2
        panel_size = '600x800'

    for i in range(panel_count):
        panel = Panel.objects.create(
            project=project,
            name=f'Panel {i + 1}',
            size=panel_size,
            price=5000.00  # Example static price
        )

        # Example components for each panel
        Component.objects.create(
            panel=panel,
            name='Breaker',
            type='breaker',
            quantity=5,
            unit_price=100.00,
            total_price=500.00
        )
        Component.objects.create(
            panel=panel,
            name='Meter',
            type='meter',
            quantity=1,
            unit_price=200.00,
            total_price=200.00
        )
