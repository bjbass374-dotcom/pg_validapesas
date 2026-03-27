import numpy as np

# Constantes
R = 8.314472
Ma = 0.02896546
Mv = 0.01801528

def saturation_vapor_pressure(T):
    # T en Kelvin (CIPM aproximado)
    A = 1.2378847e-5   # 1/K^2
    B = - 1.9121316e-2  # 1/K
    C = 33.93711047  # Adimensional
    D = - 6.3431645e3 # K
    return np.exp(A*T**2 +B*T + C  + D/T)

def calc_Z(p, T, xv):
    a0 = 1.58123e-6   # K/Pa
    a1 = -2.9331e-8  # 1/Pa
    a2 = 1.1043e-10  # 1/(K·Pa)
    b0 = 5.707e-6   # K/Pa
    b1 = -2.051e-8  # 1/Pa
    c0 = 1.9898e-4   # K/Pa
    c1 = -2.376e-6  # 1/Pa
    d  = 1.83e-11  # K^2/Pa^2
    e  = -7.65e-9  # K^2/Pa^2
    t=T-273.15 #temperatura en grados celcius
    return 1-(p/T)*(a0+a1*t+a2*t**2+(b0+b1*t)*xv+(c0+c1*t)*xv**2)+(p/T)**2*(d+e*xv**2)
       
def air_density(t, HR, p):     # T en ºC, HR en % (0% a 100%), p en mbar
    T=t+273.15 #temperatura en Kelvin K
    P=p*100 #presion en Pascales Pa    
    h=HR/100 #humedad en tanto por uno 0-1 
    
    alfa = 1.00062 #adimensional
    beta = 3.14e-8 #1/Pa
    gama = 5.6e-7  #1/K^2
    
    f= alfa+beta*P+gama*t**2 #admin
    p_sv = saturation_vapor_pressure(T)
    xv = h * f * p_sv / P
    Z = calc_Z(P,T,xv)  # aproximación (puedes mejorar esto)
    Xco2=0.0004

    rho = ((p * (1-0.3780*xv)) / (Z * R * T)) * (28.96546+12.011*(Xco2-0.0004)) # corrije esta formula 
    return rho/10


def monte_carlo_density(t, HR, p, u_t, u_HR, u_p, N=100000):
    # Generación de muestras con las mismas unidades de entrada
    t_samples = np.random.normal(t, u_t, N)       # °C
    HR_samples = np.random.normal(HR, u_HR, N)    # %
    p_samples = np.random.normal(p, u_p, N)       # mbar

    rho_samples = [
        air_density(ti, hri, pi)
        for ti, hri, pi in zip(t_samples, HR_samples, p_samples)
    ]

    rho_mean = np.mean(rho_samples)
    u_rho = np.std(rho_samples)

    return rho_mean, u_rho

#densidad = air_density(20.2,49.5,652.3)
#densidad_mean, u_densidad = monte_carlo_density(20.2,49.5,652.3, 0.5, 2, 1.50)
#print(f"densidad= {densidad} densidad_media={densidad_mean} U_densidad={u_densidad}")