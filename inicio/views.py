from django.shortcuts import render
from django.http import HttpResponse

#librerias necesarias para la API 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  # Para desarrollo
from datetime import datetime

from .serializers import DatosAmbientalesSerializer, DensidadResultadoSerializer
from .calculos.densidad_aire import air_density, monte_carlo_density
from .calculos.data_TH import TERMOHIGROMETROS

# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')  # Apunta a la plantilla hija

#vista de la API, 
class CalcularDensidadAPIView(APIView):
    """
    API Endpoint para calcular densidad del aire con incertidumbre
    """
    permission_classes = [AllowAny]  # Permite acceso sin autenticación (para pruebas)
    
    def post(self, request):
        """
        Método POST: recibe datos ambientales, devuelve densidad calculada
        """
        # 1. Validar datos de entrada con el serializer
        serializer = DatosAmbientalesSerializer(data=request.data)
        
        if not serializer.is_valid():
            # Si hay errores de validación, devolverlos
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Extraer datos validados
        datos = serializer.validated_data
        t_ini = datos['t_ini']
        t_fin = datos['t_fin']
        h_ini = datos['h_ini']
        h_fin = datos['h_fin']
        p_ini = datos['p_ini']
        p_fin = datos['p_fin']
        
        # ---- Calcular promedios ----
        t_prom = (t_ini + t_fin) / 2
        h_prom = (h_ini + h_fin) / 2
        p_prom = (p_ini + p_fin) / 2
        
        
        # ---- Obtener el termohigrómetro seleccionado ----
        termo_id = datos.get('termo_id')
        if termo_id not in TERMOHIGROMETROS:
            return Response(
                {'error': f'Termohigrómetro "{termo_id}" no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        termo_data = TERMOHIGROMETROS[termo_id]
        
        # Usar las incertidumbres del termohigrómetro (sobrescriben valores por defecto)
        u_t = termo_data['u_t']
        u_h = termo_data['u_hr']
        u_p = termo_data['u_p']


        
        # 4. Ejecutar cálculos segun el codigo python en densidad_aire.py
        try:
            densidad_puntual = air_density(t_prom, h_prom, p_prom)
            densidad_media, incertidumbre = monte_carlo_density(
                t_prom, h_prom, p_prom, u_t, u_h, u_p, N=10000
            )
        except Exception as e:
            return Response(
                {'error': f'Error en cálculo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        
        # 5. Preparar respuesta
        resultado = {
            'densidad_puntual': round(float(densidad_puntual), 8),
            'densidad_media': round(float(densidad_media), 8),
            'incertidumbre': round(float(incertidumbre), 8),
            't_prom': round(t_prom, 2),
            'h_prom': round(h_prom, 2),
            'p_prom': round(p_prom, 2),
            'termo_id': termo_id,
            'u_t_used': u_t,
            'u_h_used': u_h,
            'u_p_used': u_p,
            'timestamp': datetime.now()
        }
        
        # 6. Serializar y devolver respuesta
        resultado_serializer = DensidadResultadoSerializer(resultado)
        return Response(resultado_serializer.data, status=status.HTTP_200_OK)
    
    def get(self, request):
        """
        Método GET: información sobre la API
        """
        return Response({
            'nombre': 'API de Cálculo de Densidad del Aire',
            'version': '1.0.0',
            'descripcion': 'Calcula la densidad del aire usando CIPM-2007 y Monte Carlo',
            'endpoints': {
                'POST /api/calcular-densidad/': 'Enviar datos ambientales y obtener densidad'
            },
            'ejemplo_body': {
                't_ini': 20.5,
                't_fin': 21.0,
                'h_ini': 48.9,
                'h_fin': 49.5,
                'p_ini': 651.8,
                'p_fin': 652.0
            }
        })