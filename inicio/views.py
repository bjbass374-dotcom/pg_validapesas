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

from .calculos.patrones import PATRONES
from .calculos.masa_abba import monte_carlo_masa_abba

# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')  # Apunta a la plantilla hija

#vista de la API, 
class CalcularDensidadAPIView(APIView):
    def post(self, request):
        serializer = DatosAmbientalesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        datos = serializer.validated_data

        # --- 1. Datos ambientales y termohigrómetro (para incertidumbres) ---
        t_ini = datos['t_ini']
        t_fin = datos['t_fin']
        h_ini = datos['h_ini']
        h_fin = datos['h_fin']
        p_ini = datos['p_ini']
        p_fin = datos['p_fin']

        termo_id = datos.get('termo_id')
        if termo_id not in TERMOHIGROMETROS:
            return Response({'error': f'Termohigrómetro "{termo_id}" no encontrado'}, status=400)
        termo_data = TERMOHIGROMETROS[termo_id]
        u_t = termo_data['u_t']
        u_h = termo_data['u_hr']
        u_p = termo_data['u_p']

        # Promedios ambientales (los usamos tanto para densidad como para masa)
        t_prom = (t_ini + t_fin) / 2
        h_prom = (h_ini + h_fin) / 2
        p_prom = (p_ini + p_fin) / 2

        # --- 2. Datos del patrón (desde diccionario) ---
        patron_id = datos['patron_id']
        nominal_patron = datos['nominal_patron']
        unidades_patron = datos['unidades_patron']

        clave_pesa = f"{int(nominal_patron)}{unidades_patron}"   # ej. "10g"

        if patron_id not in PATRONES:
            return Response({'error': f'Patrón {patron_id} no encontrado'}, status=400)
        patron_data = PATRONES[patron_id]
        if clave_pesa not in patron_data['pesas']:
            return Response({'error': f'Valor nominal {clave_pesa} no disponible'}, status=400)

        pesa = patron_data['pesas'][clave_pesa]
        m_cr = pesa['m_cr']          # kg
        u_cr = pesa['u_cr']          # kg
        rho_r = pesa['rho_r']        # kg/m³
        u_rho_r = pesa['u_rho_r']    # kg/m³

        # --- 3. Datos del DUT ---
        rho_t = datos['rho_t']        # kg/m³
        u_rho_t = datos['u_rho_t']    # kg/m³

        # --- 4. Mediciones ---
        mediciones = datos['mediciones']
        num_ciclos = datos.get('num_ciclos', len(mediciones))
        mediciones = mediciones[:num_ciclos]

        # Convertir a kg si la unidad del patrón no es kg
        if unidades_patron == 'mg':
            factor = 1e-6   # mg -> kg
            mediciones = [[v * factor for v in ciclo] for ciclo in mediciones]
        elif unidades_patron == 'g':
            factor = 0.001   # g -> kg
            mediciones = [[v * factor for v in ciclo] for ciclo in mediciones]
        # Si es 'kg', no se modifica

        # --- 5. Cálculo de masa (ahora sí tenemos u_t, u_h, u_p) ---
        m_ct_mean, m_ct_std = monte_carlo_masa_abba(
            m_cr, u_cr,
            rho_t, u_rho_t,
            rho_r, u_rho_r,
            t_prom, h_prom, p_prom,
            u_t, u_h, u_p,
            mediciones,
            N=100000
        )

        # --- 6. Cálculo de densidad ---
        try:
            densidad_puntual = air_density(t_prom, h_prom, p_prom)
            densidad_media, incertidumbre = monte_carlo_density(
                t_prom, h_prom, p_prom, u_t, u_h, u_p, N=100000
            )
        except Exception as e:
            return Response({'error': f'Error en cálculo de densidad: {str(e)}'}, status=500)

        # --- 7. Preparar respuesta ---
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
            'm_ct': round(float(m_ct_mean), 8) if m_ct_mean is not None else None,
            'u_m_ct': round(float(m_ct_std), 8) if m_ct_std is not None else None,
            'timestamp': datetime.now(),
            'num_ciclos': num_ciclos,
        }

        resultado_serializer = DensidadResultadoSerializer(resultado)
        return Response(resultado_serializer.data, status=200)
    