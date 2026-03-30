import numpy as np
from masa_abba import monte_carlo_masa_abba

# Definir mediciones (4 ciclos)
mediciones = [
    [1.0002, 1.0004, 1.0004, 1.0002],   # Ciclo 1 (A1,B1,B2,A2)
    [1.0001, 1.0003, 1.0003, 1.0001],   # Ciclo 2
    [1.0003, 1.0005, 1.0005, 1.0003],   # Ciclo 3
    [1.0002, 1.0004, 1.0004, 1.0002]    # Ciclo 4
]

# Parámetros de entrada
m_cr = 1.0         # kg
u_cr = 0.000005    # 5 mg

rho_t = 7800.0     # kg/m³
u_rho_t = 50.0

rho_r = 8000.0     # kg/m³
u_rho_r = 50.0

t_avg = 20.0       # °C
h_avg = 50.0       # %
p_avg = 1013.25    # mbar

u_t = 0.2
u_h = 2.0
u_p = 1.0

# Llamar a la función (usar N=5000 para rapidez, pero N=10000 es mejor)
m_ct_mean, m_ct_std = monte_carlo_masa_abba(
    m_cr, u_cr, rho_t, u_rho_t, rho_r, u_rho_r,
    t_avg, h_avg, p_avg, u_t, u_h, u_p,
    mediciones, N=5000
)

print(f"Resultados Monte Carlo (N=5000):")
print(f"  Masa convencional del DUT: {m_ct_mean:.8f} kg")
print(f"  Incertidumbre estándar:    {m_ct_std:.8f} kg")
print(f"  Incertidumbre expandida (k=2): {2*m_ct_std:.8f} kg")