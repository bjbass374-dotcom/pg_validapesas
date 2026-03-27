# apps/inicio/urls.py
from django.urls import path
from . import views
from .views import CalcularDensidadAPIView

urlpatterns = [
    # Vista tradicional (HTML)
    path('', views.inicio, name='inicio'),
    
    # API endpoint
    path('api/calcular_densidad/', CalcularDensidadAPIView.as_view(), name='api_calcular_densidad'),
]