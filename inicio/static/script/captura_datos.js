// static/script.js

// Función de presión de vapor de saturación (CIPM aproximado)
function saturationVaporPressure(T) {
    // T en Kelvin
    const A = 1.2378847e-5;
    const B = -1.9121316e-2;
    const C = 33.93711047;
    const D = -6.3431645e3;
    return Math.exp(A * T * T + B * T + C + D / T);
}

// Función de compresibilidad Z
function calcZ(p, T, xv) {
    // p en Pa, T en Kelvin, xv fracción molar de vapor
    const t = T - 273.15; // temperatura en °C
    const a0 = 1.58123e-6;
    const a1 = -2.9331e-8;
    const a2 = 1.1043e-10;
    const b0 = 5.707e-6;
    const b1 = -2.051e-8;
    const c0 = 1.9898e-4;
    const c1 = -2.376e-6;
    const d = 1.83e-11;
    const e = -7.65e-9;
    
    return 1 - (p / T) * (a0 + a1 * t + a2 * t * t + (b0 + b1 * t) * xv + (c0 + c1 * t) * xv * xv) + 
           (p / T) * (p / T) * (d + e * xv * xv);
}

// Función principal de densidad del aire
function airDensity(t, HR, p) {
    // t en °C, HR en % (0-100), p en mbar
    const T = t + 273.15; // temperatura en Kelvin
    const P = p * 100;    // presión en Pascales
    const h = HR / 100;    // humedad en tanto por uno
    
    // Parámetros de mejora
    const alfa = 1.00062;
    const beta = 3.14e-8;
    const gama = 5.6e-7;
    
    const f = alfa + beta * P + gama * t * t;
    const p_sv = saturationVaporPressure(T);
    const xv = h * f * p_sv / P;
    const Z = calcZ(P, T, xv);
    const Xco2 = 0.0004;
    
    // R constante de los gases (J/(mol·K))
    const R = 8.314472;
    
    const rho = ((p * (1 - 0.3780 * xv)) / (Z * R * T)) * (28.96546 + 12.011 * (Xco2 - 0.0004));
    return rho / 10; // ajuste de unidades
}

// Función de Monte Carlo para incertidumbre
function monteCarloDensity(t, HR, p, u_t, u_HR, u_p, N = 100000) {
    const samples = [];
    
    for (let i = 0; i < N; i++) {
        // Generar muestras con distribución normal
        // Usamos el método de Box-Muller para generar números aleatorios normales
        const t_sample = t + u_t * boxMuller();
        const HR_sample = HR + u_HR * boxMuller();
        const p_sample = p + u_p * boxMuller();
        
        // Calcular densidad para cada muestra
        const rho_sample = airDensity(t_sample, HR_sample, p_sample);
        samples.push(rho_sample);
    }
    
    // Calcular media y desviación estándar
    const mean = samples.reduce((a, b) => a + b, 0) / samples.length;
    const variance = samples.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / samples.length;
    const std = Math.sqrt(variance);
    
    return { mean: mean, std: std };
}

// Función auxiliar Box-Muller para generar números aleatorios normales
function boxMuller() {
    let u = 0, v = 0;
    while (u === 0) u = Math.random();
    while (v === 0) v = Math.random();
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}



// Función principal al hacer clic en el botón
function ejecutarCalculo() {
    console.log("Botón CALCULAR presionado");
    
    // Obtener valores de condiciones iniciales
    const t_ini = parseFloat(document.getElementById('ini_temp').value);
    const h_ini = parseFloat(document.getElementById('ini_hum').value);
    const p_ini = parseFloat(document.getElementById('ini_pres').value);
    
    // Obtener valores de condiciones finales
    const t_fin = parseFloat(document.getElementById('fin_temp').value);
    const h_fin = parseFloat(document.getElementById('fin_hum').value);
    const p_fin = parseFloat(document.getElementById('fin_pres').value);
    
    // Validar que todos los campos estén completos
    if (isNaN(t_ini) || isNaN(h_ini) || isNaN(p_ini) || 
        isNaN(t_fin) || isNaN(h_fin) || isNaN(p_fin)) {
        alert('Por favor complete todos los campos de condiciones ambientales.');
        return;
    }
    
    // Calcular promedios
    const t_prom = (t_ini + t_fin) / 2;
    const h_prom = (h_ini + h_fin) / 2;
    const p_prom = (p_ini + p_fin) / 2;
    
    console.log("Promedios calculados:");
    console.log(`t_prom = ${t_prom.toFixed(2)} °C`);
    console.log(`h_prom = ${h_prom.toFixed(2)} %`);
    console.log(`p_prom = ${p_prom.toFixed(2)} mbar`);
    
    // Incertidumbres fijas (puedes ajustar estos valores)
    const u_t = 0.5;      // °C
    const u_h = 2.0;      // %
    const u_p = 1.5;      // mbar
    
    // Calcular densidad puntual
    const densidad_puntual = airDensity(t_prom, h_prom, p_prom);
    
    // Calcular densidad con Monte Carlo e incertidumbre
    const resultado = monteCarloDensity(t_prom, h_prom, p_prom, u_t, u_h, u_p);
    
    console.log("Resultados:");
    console.log(`Densidad puntual: ${densidad_puntual.toFixed(6)} kg/m³`);
    console.log(`Densidad media (Monte Carlo): ${resultado.mean.toFixed(6)} kg/m³`);
    console.log(`Incertidumbre (k=1): ${resultado.std.toFixed(6)} kg/m³`);
    
    // Mostrar resultados en los campos de texto
    document.getElementById('resultado_1').value = densidad_puntual.toFixed(6);
    document.getElementById('resultado_2').value = resultado.mean.toFixed(6);
    document.getElementById('resultado_3').value = resultado.std.toFixed(6);
}