# apps/inicio/serializers.py
from rest_framework import serializers

class DatosAmbientalesSerializer(serializers.Serializer):
    # Campos ambientales
    t_prom = serializers.FloatField()
    h_prom = serializers.FloatField()
    p_prom = serializers.FloatField()
    termo_id = serializers.CharField()

    # Campos del patrón
    patron_id = serializers.CharField()
    nominal_patron = serializers.FloatField()
    unidades_patron = serializers.CharField()

    # Campos del DUT
    rho_t = serializers.FloatField()
    u_rho_t = serializers.FloatField()

    # Mediciones
    mediciones = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField()),
        required=True
    )
    num_ciclos = serializers.IntegerField(required=False, default=8)
    


class DensidadResultadoSerializer(serializers.Serializer):
    """
    Serializer para los resultados (lo que devuelve la API)
    """
    densidad_puntual = serializers.FloatField(help_text="Densidad del aire puntual (kg/m³)")
    densidad_media = serializers.FloatField(help_text="Densidad media por Monte Carlo (kg/m³)")
    incertidumbre = serializers.FloatField(help_text="Incertidumbre expandida (k=1)")
    t_prom = serializers.FloatField(help_text="Temperatura promedio (°C)")
    h_prom = serializers.FloatField(help_text="Humedad promedio (%)")
    p_prom = serializers.FloatField(help_text="Presión promedio (mbar)")
    termo_id = serializers.CharField()
    u_t_used = serializers.FloatField()
    u_h_used = serializers.FloatField()
    u_p_used = serializers.FloatField()
    timestamp = serializers.DateTimeField(help_text="Momento del cálculo")
        # Nuevos campos para masa
    m_ct = serializers.FloatField(required=False)
    u_m_ct = serializers.FloatField(required=False)