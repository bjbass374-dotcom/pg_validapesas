import numpy as np
from masa_abba import monte_carlo_masa_abba

# Definir mediciones (4 ciclos)
mediciones_g = [
    [0, 0.000089, 0.00009, 0.000001],   # Ciclo 1 (A1,B1,B2,A2)
    [0.000002, 0.000089, 0.000087, 0.000002],   # Ciclo 2
    [0.00000, 0.000087, 0.000089, 0.000002],   # Ciclo 3    # Ciclo 4
]

mediciones_kg = [
    [0, 8.9e-8, 9.0e-8, 1e-9],
    [2e-9, 8.9e-8, 8.7e-8, 2e-9],
    [0, 8.7e-8, 8.9e-8, 2e-9]
]

# Parámetros de entrada
m_cr = 0.0100000190         # kg
u_cr = 0.0000000100    # 5 mg

rho_t = 7950.0     # kg/m³
u_rho_t = 70.0

rho_r = 8044.0     # kg/m³
u_rho_r = 5.0

t_avg = 20.5      # °C
h_avg = 50.1       # %
p_avg = 651.5    # mbar

u_t = 0.2
u_h = 2.0
u_p = 1.0

# Llamar a la función (usar N=5000 para rapidez, pero N=10000 es mejor)
m_ct_mean, m_ct_std = monte_carlo_masa_abba(
    m_cr, u_cr, rho_t, u_rho_t, rho_r, u_rho_r,
    t_avg, h_avg, p_avg, u_t, u_h, u_p,
    mediciones_kg, N=10000
)

print(f"Resultados Monte Carlo (N=5000):")
print(f"  Masa convencional del DUT: {m_ct_mean:.8f} kg")
print(f"  Incertidumbre estándar:    {m_ct_std:.8f} kg")
print(f"  Incertidumbre expandida (k=2): {2*m_ct_std:.8f} kg")