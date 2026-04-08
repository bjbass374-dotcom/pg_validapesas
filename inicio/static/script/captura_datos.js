// static/script/captura_datos.js

/**
 * Función principal que se ejecuta al hacer clic en CALCULAR
 */
async function ejecutarCalculo() {
    console.log("🚀 Botón CALCULAR presionado");
    
    // ========== 1. CAPTURAR DATOS DEL DOM ==========
    // Capturar condiciones iniciales
    const t_ini = parseFloat(document.getElementById('ini_temp').value);
    const h_ini = parseFloat(document.getElementById('ini_hum').value);
    const p_ini = parseFloat(document.getElementById('ini_pres').value);
    
    // Capturar condiciones finales
    const t_fin = parseFloat(document.getElementById('fin_temp').value);
    const h_fin = parseFloat(document.getElementById('fin_hum').value);
    const p_fin = parseFloat(document.getElementById('fin_pres').value);
    const termo_id = document.getElementById('sel_termo').value   // solo esto nuevo
    
    //obtener datos de densidad e incertidumbre de densidad del DUT
    const unidad_dut = document.getElementById('sel_unidades_dut').value; 
    const rho_t = parseFloat(document.getElementById('dens_dut').value);
    const u_rho_t = parseFloat(document.getElementById('udens_dut').value);

    // Obtener datos del patrón
    const patron_id = document.getElementById('sel_patron').value;
    const nominal_patron = parseInt(document.getElementById('sel_nominal_patron').value);
    const unidades_patron = document.getElementById('sel_unidades_patron').value;

    //obtener los datos de las mediciones 
    const num_ciclos = parseInt(document.getElementById('num_ciclos').value) || 8;
    const mediciones = [];


    // Obtener el factor de conversión a kg
    const unidad = document.getElementById('sel_unidades_dut').value;
    let factor = 1;   // por defecto kg
    if (unidad === 'g') {
        factor = 0.001;   // 1 g = 0.001 kg
    } else if (unidad === 'mg') {
        factor = 0.000001; // 1 mg = 1e-6 kg
    }

    // Ahora recorremos los ciclos y convertimos cada valor
    const lecturas = [];  // Para almacenar las mediciones convertidas
    for (let i = 0; i < num_ciclos; i++) {
        const A1 = (parseFloat(document.querySelectorAll('.val-a1')[i]?.value) || 0) * factor;
        const B1 = (parseFloat(document.querySelectorAll('.val-b1')[i]?.value) || 0) * factor;
        const B2 = (parseFloat(document.querySelectorAll('.val-b2')[i]?.value) || 0) * factor;
        const A2 = (parseFloat(document.querySelectorAll('.val-a2')[i]?.value) || 0) * factor;

        mediciones.push([A1, B1, B2, A2]);
    }
    
    // ========== 2. VALIDAR DATOS ==========
    // Verificar que todos los campos estén completos
    if (isNaN(t_ini) || isNaN(h_ini) || isNaN(p_ini) || 
        isNaN(t_fin) || isNaN(h_fin) || isNaN(p_fin)) {
        
        mostrarEnDebug("❌ Error: Complete todos los campos de condiciones ambientales");
        alert('Por favor complete todos los campos de condiciones ambientales (iniciales y finales).');
        return;
    }
    
    // ========== 3. CALCULAR PROMEDIOS ==========
    const t_prom = (t_ini + t_fin) / 2;
    const h_prom = (h_ini + h_fin) / 2;
    const p_prom = (p_ini + p_fin) / 2;
    
    // Mostrar promedios en el área de depuración
    mostrarEnDebug(`
        ✅ Datos capturados:<br>
        📊 Temperatura promedio: ${t_prom.toFixed(2)} °C<br>
        💧 Humedad promedio: ${h_prom.toFixed(2)} %<br>
        🌡️ Presión promedio: ${p_prom.toFixed(2)} mbar<br>
        ⏳ Enviando petición a la API...
    `);
    
    // ========== 4. PREPARAR DATOS PARA LA API ==========
    const datosParaAPI = {
        // Datos ambientales
        t_prom, h_prom, p_prom,
        termo_id,
        
        // Datos del patrón
        patron_id,
        nominal_patron,
        unidades_patron,
        
        // Datos del DUT
        rho_t,
        u_rho_t,
        
        // Mediciones
        mediciones,
        num_ciclos
    };
    
    // Mostrar "Calculando..." en los campos de resultado
    document.getElementById('resultado_1').value = "Calculando...";
    document.getElementById('resultado_2').value = "Calculando...";
    document.getElementById('resultado_3').value = "Calculando...";
    document.getElementById('resultado_4').value = "Calculando...";
    document.getElementById('resultado_5').value = "Calculando...";
    
    // ========== 5. ENVIAR PETICIÓN A LA API ==========
    try {
        // Obtener token CSRF (necesario para POST en Django)
        const csrftoken = getCookie('csrftoken');
        
        // Realizar petición fetch
        const response = await fetch('/api/calcular_densidad/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datosParaAPI)
        });
        
        // ========== 6. PROCESAR RESPUESTA ==========
        if (!response.ok) {
            // Si hay error HTTP, intentar obtener mensaje de error
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP: ${response.status}`);
        }
        
        // Convertir respuesta a JSON
        const resultado = await response.json();
        
        // ========== 7. ACTUALIZAR INTERFAZ CON RESULTADOS ==========
        // Mostrar resultados en los campos de texto
        document.getElementById('resultado_1').value = resultado.densidad_puntual;
        document.getElementById('resultado_2').value = resultado.densidad_media;
        document.getElementById('resultado_3').value = resultado.incertidumbre;
        
        // Mostrar masa convencional convertida
        if (resultado.m_ct !== null && resultado.m_ct !== undefined) {
            const m_ct_conv = convertirDesdeKg(resultado.m_ct, unidad_dut);
            document.getElementById('resultado_4').value = `${m_ct_conv.toFixed(6)} ${unidad_dut}`;
        } else {
            document.getElementById('resultado_4').value = "Error";
        }

        // Mostrar incertidumbre convertida a mg (siempre en mg)
        const u_m_ct_conv = convertirDesdeKg(resultado.u_m_ct, "mg");
        document.getElementById('resultado_5').value = `${u_m_ct_conv.toFixed(6)} mg`;
 
                
        // Mostrar resultados y éxito en el área de depuración
        mostrarEnDebug(`
            ✅ CÁLCULO EXITOSO<br><br>
            📊 DENSIDAD DEL AIRE:<br>
            &nbsp;&nbsp;📦 Puntual: ${resultado.densidad_puntual} kg/m³<br>
            &nbsp;&nbsp;🎲 Media (Monte Carlo): ${resultado.densidad_media} kg/m³<br>
            &nbsp;&nbsp;📊 Incertidumbre (k=1): ${resultado.incertidumbre} kg/m³<br>
            ⚖️ MASA CONVENCIONAL:<br>
            &nbsp;&nbsp;🔹 m_ct: ${resultado.m_ct !== undefined ? resultado.m_ct : '---'} kg<br>
            &nbsp;&nbsp;🔹 u(m_ct): ${resultado.u_m_ct !== undefined ? resultado.u_m_ct : '---'} kg<br>
            &nbsp;&nbsp;🔹 Incertidumbre expandida (k=2): ${resultado.u_m_ct !== undefined ? (2 * resultado.u_m_ct).toFixed(8) : '---'} kg<br><br>
            🌡️ CONDICIONES AMBIENTALES PROMEDIO:<br>
            &nbsp;&nbsp;🌡️ Temperatura: ${resultado.t_prom} °C<br>
            &nbsp;&nbsp;💧 Humedad: ${resultado.h_prom} %<br>
            &nbsp;&nbsp;🌡️ Presión: ${resultado.p_prom} mbar<br><br>
            🔧 DISPOSITIVOS AUXILIARES:<br>
            &nbsp;&nbsp;🌡️ Termohigrómetro: ${resultado.termo_id}<br>
            &nbsp;&nbsp;📊 u_T = ${resultado.u_t_used} °C &nbsp;|&nbsp; u_HR = ${resultado.u_h_used} % &nbsp;|&nbsp; u_P = ${resultado.u_p_used} mbar<br><br>
            ⏱️ Timestamp: ${resultado.timestamp}
        `);
        
        console.log("Resultado completo:", resultado);
        
    } catch (error) {
        // ========== 8. MANEJAR ERRORES ==========
        console.error('❌ Error:', error);
        
        // Mostrar error en los campos de resultado
        document.getElementById('resultado_1').value = "Error";
        document.getElementById('resultado_2').value = "Error";
        document.getElementById('resultado_3').value = "Error";
        
        // Mostrar error en el área de depuración
        mostrarEnDebug(`
            ❌ ERROR:<br>
            ${error.message}<br>
            🔄 Verifique que el servidor Django esté corriendo<br>
            🔍 Revise la consola del navegador para más detalles
        `);
        
        alert('Error al calcular: ' + error.message);
    }
}

/**
 * Función auxiliar para mostrar mensajes en el área de depuración
 */
function mostrarEnDebug(mensaje) {
    const debugElement = document.getElementById('debug-values');
    if (debugElement) {
        debugElement.innerHTML = mensaje;
    }
}

/**
 * Función auxiliar para obtener la cookie CSRF
 * Necesaria para peticiones POST en Django
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Función opcional: Validar que todos los campos de medición estén llenos
 * Puedes implementarla si necesitas validar los valores de la tabla
 */
function validarMediciones() {
    const ciclos = parseInt(document.getElementById('num_ciclos').value) || 8;
    const valoresA1 = document.querySelectorAll('.val-a1');
    const valoresB1 = document.querySelectorAll('.val-b1');
    const valoresB2 = document.querySelectorAll('.val-b2');
    const valoresA2 = document.querySelectorAll('.val-a2');
    
    // Verificar que todos los campos necesarios estén llenos
    let todosLlenos = true;
    const todosLosCampos = [...valoresA1, ...valoresB1, ...valoresB2, ...valoresA2];
    
    for (let i = 0; i < ciclos; i++) {
        if (todosLosCampos[i] && todosLosCampos[i].value === '') {
            todosLlenos = false;
            break;
        }
    }
    
    return todosLlenos;
}

// Función auxiliar para convertir de kg a la unidad deseada
function convertirDesdeKg(valor_kg, unidad) {
    switch (unidad) {
        case 'mg': return valor_kg * 1_000_000;   // kg → mg
        case 'g':  return valor_kg * 1_000;       // kg → g
        case 'kg': return valor_kg;               // kg → kg
        default:   return valor_kg;
    }
}