# apps/inicio/serializers.py
from rest_framework import serializers

class DatosAmbientalesSerializer(serializers.Serializer):
    """
    Serializer para los datos de entrada (lo que llega del frontend)
    """
    t_ini = serializers.FloatField(help_text="Temperatura inicial (°C)")
    t_fin = serializers.FloatField(help_text="Temperatura final (°C)")
    h_ini = serializers.FloatField(help_text="Humedad inicial (%)")
    h_fin = serializers.FloatField(help_text="Humedad final (%)")
    p_ini = serializers.FloatField(help_text="Presión inicial (mbar)")
    p_fin = serializers.FloatField(help_text="Presión final (mbar)")
    

    # Incertidumbres: pueden ser opcionales porque vendrán del termohigrómetro
    u_t = serializers.FloatField(required=False, default=0.5)
    u_h = serializers.FloatField(required=False, default=2.0)
    u_p = serializers.FloatField(required=False, default=1.0)

    # Campo nuevo: termohigrómetro seleccionado
    termo_id = serializers.CharField(required=True, help_text="ID del termohigrómetro")
    
    def validate_t_ini(self, value):
        """Validación personalizada: temperatura debe estar entre -50 y 100°C"""
        if value < -50 or value > 100:
            raise serializers.ValidationError("Temperatura fuera de rango (-50 a 100°C)")
        return value
    
    def validate_h_ini(self, value):
        """Validación: humedad entre 0 y 100%"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Humedad debe estar entre 0 y 100%")
        return value


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