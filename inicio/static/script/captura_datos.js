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
        t_ini: t_ini,
        t_fin: t_fin,
        h_ini: h_ini,
        h_fin: h_fin,
        p_ini: p_ini,
        p_fin: p_fin,
        termo_id: termo_id
    };
    
    // Mostrar "Calculando..." en los campos de resultado
    document.getElementById('resultado_1').value = "Calculando...";
    document.getElementById('resultado_2').value = "Calculando...";
    document.getElementById('resultado_3').value = "Calculando...";
    
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
        
        // Mostrar éxito en el área de depuración
        mostrarEnDebug(`
            ✅ Cálculo exitoso!<br>
            📦 Densidad puntual: ${resultado.densidad_puntual} kg/m³<br>
            🎲 Densidad media (Monte Carlo): ${resultado.densidad_media} kg/m³<br>
            📊 Incertidumbre: ${resultado.incertidumbre} kg/m³<br>
            🌡️ Temperatura promedio: ${resultado.t_prom} °C<br>
            💧 Humedad promedio: ${resultado.h_prom} %<br>
            🌡️ Presión promedio: ${resultado.p_prom} mbar
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