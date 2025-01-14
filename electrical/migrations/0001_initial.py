# Generated by Django 5.0.8 on 2024-12-07 11:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Panel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Panel name (e.g., Main Panel, Sub Panel)', max_length=255)),
                ('size', models.CharField(help_text='Panel size (e.g., 400mm x 600mm)', max_length=50)),
                ('price', models.DecimalField(decimal_places=2, help_text='Total price for this panel', max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Component name (e.g., 3P Breaker, Contactor)', max_length=255)),
                ('type', models.CharField(choices=[('breaker', 'Breaker'), ('contactor', 'Contactor'), ('meter', 'Meter'), ('capacitor', 'Power Factor Capacitor'), ('push_button', 'Push Button'), ('indicator', 'Indication Light'), ('fan', 'Fan'), ('cam_switch', 'Cam Switch'), ('other', 'Other')], help_text='Component type', max_length=50)),
                ('quantity', models.PositiveIntegerField(default=1, help_text='Number of components used')),
                ('unit_price', models.DecimalField(decimal_places=2, help_text='Price per unit of this component', max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, help_text='Total price for the component', max_digits=10)),
                ('specifications', models.JSONField(blank=True, help_text='Additional specs (e.g., amperage, voltage)', null=True)),
                ('panel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='electrical.panel')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Project name', max_length=255)),
                ('sld_file', models.FileField(blank=True, help_text='Uploaded SLD file', null=True, upload_to='slds/')),
                ('description', models.TextField(blank=True, help_text='Load description', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_panels_price', models.DecimalField(decimal_places=2, default=0.0, help_text='Total price for panels', max_digits=12)),
                ('total_components_price', models.DecimalField(decimal_places=2, default=0.0, help_text='Total price for components', max_digits=12)),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, help_text='Overall project price', max_digits=12)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pricing', to='electrical.project')),
            ],
        ),
        migrations.AddField(
            model_name='panel',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='panels', to='electrical.project'),
        ),
    ]
