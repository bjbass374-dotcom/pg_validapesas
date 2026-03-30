# apps/inicio/calculos/masa_abba.py
import numpy as np
from densidad_aire import air_density

def monte_carlo_masa_abba(m_cr, u_cr, rho_t, u_rho_t, rho_r, u_rho_r,
                          t_avg, h_avg, p_avg, u_t, u_h, u_p,
                          mediciones, N=10000):
    """
    Calcula masa convencional e incertidumbre por Monte Carlo usando el método ABBA.
    
    Parámetros:
        m_cr, u_cr       : masa patrón e incertidumbre estándar (kg)
        rho_t, u_rho_t   : densidad del DUT e incertidumbre (kg/m³)
        rho_r, u_rho_r   : densidad del patrón e incertidumbre (kg/m³)
        t_avg, h_avg, p_avg : condiciones ambientales promedio (°C, %, mbar)
        u_t, u_h, u_p    : incertidumbres estándar de las condiciones ambientales
        mediciones       : lista de ciclos, cada ciclo es [A1, B1, B2, A2]
                           (todas en las mismas unidades, preferiblemente kg)
        N                : número de iteraciones Monte Carlo (default 10000)
    
    Devuelve:
        m_ct_mean, m_ct_std : media y desviación estándar de la masa convencional (kg)
    """
    n_ciclos = len(mediciones)
    if n_ciclos == 0:
        return None, None

    # ---- 1. Calcular diferencias observadas ΔI_i y su desviación estándar ----
    delta_I_obs = []
    for ciclo in mediciones:
        A1, B1, B2, A2 = ciclo
        delta_I = (B1 + B2 - A1 - A2) / 2.0
        delta_I_obs.append(delta_I)
    delta_I_obs = np.array(delta_I_obs)

    # Desviación estándar muestral de las diferencias (tipo A)
    if n_ciclos >= 2:
        s_delta_I = np.std(delta_I_obs, ddof=1)   # estimación de σ_ΔI
    else:
        # Con un solo ciclo no se puede estimar la variabilidad; se asume cero o se lanza advertencia.
        # Aquí optamos por asumir que no hay variabilidad (incertidumbre tipo A = 0)
        # pero sería mejor si se proporciona una incertidumbre tipo B.
        s_delta_I = 0.0

    # ---- 2. Generar muestras de las variables de entrada ----
    np.random.seed()   # opcional: fijar semilla para reproducibilidad

    m_cr_samples = np.random.normal(m_cr, u_cr, N)
    rho_t_samples = np.random.normal(rho_t, u_rho_t, N)
    rho_r_samples = np.random.normal(rho_r, u_rho_r, N)
    t_samples = np.random.normal(t_avg, u_t, N)
    h_samples = np.random.normal(h_avg, u_h, N)
    p_samples = np.random.normal(p_avg, u_p, N)

    # Densidad del aire para cada muestra
    rho_a_samples = np.array([air_density(t, h, p) for t, h, p in zip(t_samples, h_samples, p_samples)])

    # ---- 3. Generar muestras de las diferencias ΔI_i (con la variabilidad experimental) ----
    # Si s_delta_I es cero, entonces todas las muestras serán iguales a los valores observados.
    # Si s_delta_I > 0, generamos para cada ciclo una muestra normal independiente.
    # Resultado: matriz de tamaño (N, n_ciclos)
    delta_I_samples = np.zeros((N, n_ciclos))
    for i in range(n_ciclos):
        if s_delta_I > 0:
            delta_I_samples[:, i] = np.random.normal(delta_I_obs[i], s_delta_I, N)
        else:
            delta_I_samples[:, i] = delta_I_obs[i]   # todas iguales

    # ---- 4. Corrección por empuje (para cada muestra) ----
    rho0 = 1.2   # densidad convencional del aire (kg/m³)
    C_c_samples = (rho_a_samples - rho0) * (1.0/rho_t_samples - 1.0/rho_r_samples)   # (N,)

    # ---- 5. Diferencia en masa convencional por ciclo y promedio ----
    # Δm_ci = ΔI_i + m_cr * C_c
    # m_cr_samples * C_c_samples es (N,); lo convertimos a (N,1) para sumar a delta_I_samples (N, n_ciclos)
    Δm_c_samples = delta_I_samples + (m_cr_samples * C_c_samples)[:, np.newaxis]   # (N, n_ciclos)

    # Promedio sobre ciclos para cada muestra
    avg_Δm_c_samples = np.mean(Δm_c_samples, axis=1)   # (N,)

    # ---- 6. Masa convencional final ----
    m_ct_samples = m_cr_samples + avg_Δm_c_samples   # (N,)

    # ---- 7. Estadísticas ----
    m_ct_mean = np.mean(m_ct_samples)
    m_ct_std = np.std(m_ct_samples)

    return m_ct_mean, m_ct_std