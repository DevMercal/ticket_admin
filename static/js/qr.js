const API_BASE_URL = 'https://comedor.mercal.gob.ve/api/p1/pedidos/takeOrder'; 
const API_CONSUMO_URL = 'https://comedor.mercal.gob.ve/api/p1/pedidos/consumo'; 

// ------------------------------------------------------------------
// ## Inicialización y Token
const bodyElement = document.getElementById('page-body');

const API_TOKEN = bodyElement ? bodyElement.dataset.apiToken : null;
const resultElement = document.getElementById('result'); 
console.log(bodyElement,API_TOKEN,resultElement)
if (!API_TOKEN) {
    console.error("Error: Token de API no encontrado en la sesión (dataset-api-token).");
    // Mostrar un error visible al usuario y detener la ejecución del escáner
    if (resultElement) {
        resultElement.innerHTML = '<p class="text-red-700 font-bold">Error de Autenticación: Token de API no disponible.</p>';
    }
    // No iniciar funciones de API ni escáner
}

function onScanError(error) {
    //console.error('Error al escanear el QR: ', error);
    // Usar la variable resultElement
    if (resultElement) {
        resultElement.innerHTML = ``;
    }
}

// ------------------------------------------------------------------
// ## Funciones de API

/**
 * Realiza una solicitud GET para obtener información usando el ID del QR (Order ID).
 * @typedef {Object} orderData
 * @returns {Promise<object|null>} Los datos del recurso o null si hay un error.
 */

// CORRECCIÓN 1: Corregido error de sintaxis en 'date'
function formatOrderData(orderData) {
    
    const orderNumber = orderData.number_order;
    const totalAmount = orderData.total_amount;
    // ERROR CORREGIDO: "ordorderDataer.date_order" => "orderData.date_order"
    const date = orderData.date_order; 
    const status = orderData.order_status.status_order;
    const paymentMethod = orderData.payment_method.payment_method;
    const employeeName = orderData.employee_payment.name_employee;
    const employeePhone = orderData.employee_payment.phone_employee;
    const reference = orderData.reference; 
    const consumo = orderData.order_consumption.id_orders_consumption;
    
    
      if (consumo === 3) {
                 
       }else{
        let htmlContent = `
        <style>
            .order-summary { 
                text-align: left; 
                margin-top: 15px;
                font-size: 1.05em;
            }
            .order-summary p {
                margin: 5px 0;
            }
            .order-summary strong {
                display: inline-block;
                min-width: 130px; 
            }
            .highlight-green {
                color: #28a745; 
                font-weight: bold;
            }
            .highlight-red {
                color: #dc3545; 
                font-weight: bold;
            }
        </style>
        
        <div class="order-summary">
            <h3 style="text-align: center; margin-bottom: 20px;">Orden **N° ${orderNumber}**</h3>
            
            <p><strong>Fecha de Orden:</strong> ${date}</p>
            <p><strong>Estado:</strong> <span class="${status === 'PENDIENTE' ? 'highlight-red' : 'highlight-green'}">${status}</span></p>
            <p><strong>Monto Total:</strong> <span class="highlight-green">$ ${totalAmount}</span></p>
            
            <hr style="margin: 10px 0;">

            <h4>Detalles de Pago</h4>
            <p><strong>Método:</strong> ${paymentMethod}</p>
            <p><strong>Referencia:</strong> ${reference}</p>

            <hr style="margin: 10px 0;">
            
            <h4>Empleado (Registro)</h4>
            <p><strong>Nombre:</strong> ${employeeName}</p>
            <p><strong>Teléfono:</strong> ${employeePhone}</p>
        </div>
    `;
    return htmlContent
       }
   
}

async function getResourceInfo(orderData) {
    if (!API_TOKEN) {
        console.error("Función getResourceInfo: No se puede ejecutar sin API_TOKEN.");
        return null;
    }

    
    const { resourceId } = orderData;

    const headers = {
        'Content-Type': 'application/json',

        'Authorization': `Bearer ${API_TOKEN}` 
    };
    
    const url = `${API_BASE_URL}/${resourceId}`;
   
    console.log(url);
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: headers // Usar los headers definidos, incluyendo el token
        });

        
        if (response.status === 404) {
            throw new Error(`Recurso no encontrado (404) para ID: ${resourceId}`);
        }
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status} - ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`Respuesta GET para`, data);
        return data;
    } catch (error) {
        console.error('Error en la solicitud GET:', error);
        return null;
    }
}

/**

 * @param {orderData} orderData 
 * @returns {Promise<boolean>} True si la actualización fue exitosa, false en caso contrario.
 */
async function patchResourceStatus(orderData) {
    if (!API_TOKEN) {
        console.error("Función patchResourceStatus: No se puede ejecutar sin API_TOKEN.");
        return false;
    }
    const { resourceId } = orderData;
    // Asume que quieres cambiar un campo 'status' a '3' (consumido/completado)
    const patchData = { 
        consumption: 3
    };

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_TOKEN}` 
    };
    
   
    const url = `${API_CONSUMO_URL}/${resourceId}`;
    
    try {
        const response = await fetch(url, {
            method: 'PATCH',
            headers: headers, 
            body: JSON.stringify(patchData)
        });

        if (!response.ok) {
           
            const errorBody = await response.text(); 
            throw new Error(`Error HTTP: ${response.status} - ${response.statusText}. Detalle: ${errorBody}`);
        }

        // Si la API devuelve un código 204 (No Content) o 200 (OK), es un éxito
        // const updatedData = await response.json(); // Solo si la API devuelve contenido
        
        return true; // Éxito
    } catch (error) {
        console.error('Error en la solicitud PATCH:', error);
        
        let title = 'Error al actualizar el recurso';
        let text = error.message;
        let icon = 'error';

        //  Lógica de Estilo para Error Específico (422 - Ticket ya utilizado) 
        if (text.includes('422') && text.includes('Ticket ya utilizado')) {
            title = 'Ticket ya Consumido';
            text = 'El código QR escaneado corresponde a una orden que ya fue registrada como consumida o utilizada.';
            icon = 'warning'; // Cambiamos el ícono a advertencia para diferenciarlo de un error de red.
        }
        
        //Usar Swal.fire con estilos 
        Swal.fire({
            title: title,
            html: `<p style="font-size: 1.1em;">${text}</p>`, // Estilo en el texto
            icon: icon,
            confirmButtonText: 'Aceptar',
            confirmButtonColor: icon === 'warning' ? '#ffc107' : '#d33' // Color amarillo/rojo
        });
        
        return false; // Fallo
    }
}


/**
 * Analiza el texto plano del QR y extrae el ID de la orden.
 * @param {string} qrText El texto completo escaneado.
 * @returns {string|null} El ID numérico de la orden o null si no se encuentra.
 */
function extractOrderId(qrText) {
    // Busca "Orden: " seguido de uno o más dígitos
    const match = qrText.match(/Orden: (\d+)/);
    
    // match[1] contiene el grupo capturado (el número ID)
    return match ? match[1] : null; 
}

/// ... (Código anterior de funciones y variables)

// ------------------------------------------------------------------
// ## Lógica del Escáner y Flujo

// ------------------------------------------------------------------
// ## Lógica del Escáner y Flujo

const html5QrCode = new Html5Qrcode("reader");

// Función para inicializar el escáner
function startScanner() {
    // Si no hay token, no intentar iniciar
    if (!API_TOKEN) {
        return; 
    }

    html5QrCode.start(
        { facingMode: "environment" }, 
        { fps: 10, qrbox: 250 },
        // Callback de éxito asíncrono
        async (decodedText, decodedResult) => { 
            
            console.log(`Código escaneado: ${decodedText}`);

            // 1. **Detener el escáner** inmediatamente para procesar
            html5QrCode.stop().then(() => {
                console.log("Escáner detenido.");
            }).catch(stopErr => {
              //  console.error("Error al detener el escáner (puede que haya estado ya detenido):", stopErr);
            });
            
            const orderId = extractOrderId(decodedText);
            const orderData = {
                resourceId: orderId
            };

            // *** 1. OBTENER INFORMACIÓN DEL RECURSO (GET) ***
            const resourceInfo = await getResourceInfo(orderData);
            let order = null; 
            let htmlContent = ''; // Se declara una vez aquí
            
      
            if (resourceInfo && resourceInfo.order) {
               
                order = resourceInfo.order; 

                // 1.1. **Verificar Consumo**
                const consumptionId = Number(order.order_consumption.id_orders_consumption); 
                htmlContent = formatOrderData(order); // Generar contenido para ambos casos (3 o 2)
                
                if (consumptionId === 3) {
                    
                    console.log(`Orden N° ${order.number_order} ya está marcada como consumida (ID: 3). Muestra directo.`);
                    
                    // Mostrar el mensaje de "Ya Consumido" inmediatamente (Caso: consumption: 3)
                    await Swal.fire({
                        title: '¡Ticket ya Consumido!', 
                        html: htmlContent, 
                        icon: 'warning', 
                        confirmButtonText: 'Aceptar', 
                        allowOutsideClick: false, 
                    });
                    
                    window.location.reload(); 
                    return; 
                } 

                // 1.2. **Continuar con Confirmación** (Caso: consumption: 2)
                // El flujo continúa aquí solo si consumptionId NO es 3.
                
                let titleText = `Verificar Consumo de Orden N° ${order.number_order}`;
                let iconType = 'info';
                let confirmButtonText = 'Confirmar Consumo';
                
                // 2. Mostrar Swal de Confirmación
                const swalResult = await Swal.fire({
                    title: titleText, 
                    html: htmlContent, 
                    icon: iconType,
                    showCancelButton: true, 
                    confirmButtonText: confirmButtonText, 
                    cancelButtonText: 'Cancelar',
                    draggable: true,
                    allowOutsideClick: false, 
                    allowEscapeKey: false
                });

                // 3. Paso PATCH: Ejecutar la actualización al confirmar
                if (swalResult.isConfirmed) {
                    console.log("Confirmación recibida. Iniciando solicitud PATCH...");
                    
                    const patchSuccess = await patchResourceStatus(orderData);

                    if (patchSuccess) {
                        await Swal.fire({
                            title: '¡Consumo Confirmado!',
                            text: 'El estado del recurso ha sido actualizado con éxito.',
                            icon: 'success',
                            confirmButtonText: 'Aceptar', 
                            allowOutsideClick: false,
                        });
                        window.location.reload(); 
                    } else {
                        // Si el PATCH falló (ej. por error 422 manejado internamente)
                        startScanner(); 
                    }
                } else {
                    // Acción cancelada por el usuario
                    console.log("Acción cancelada por el usuario. Reiniciando escáner.");
                    Swal.fire('Cancelado', 'La operación de actualización fue cancelada.', 'info').then(() => {
                        startScanner(); 
                    });
                }
                
            } else {
            
                
                let errorHtml = `<p class="text-red-500">No se pudo obtener la información para el ID: ${orderId}. Puede que no exista o haya un error de red/API.</p>`;
                
                await Swal.fire({
                    title: `Error en Orden: ${orderId}`,
                    html: errorHtml, 
                    icon: 'error',
                    showCancelButton: false, 
                    confirmButtonText: 'Aceptar', 
                    draggable: true,
                    allowOutsideClick: false, 
                    allowEscapeKey: false
                });

                // Reiniciar el escáner tras el error
                startScanner();
            }
        },
        onScanError
    ).catch((err) => {
        // Manejo de errores de inicio de cámara (ej. permisos)
        if (resultElement) {
             resultElement.innerHTML = `<p class="text-red-700 font-bold">Error al iniciar la cámara: Verifique permisos o dispositivo. Detalle: ${err}</p>`;
        }
    });
}

// Iniciar el escáner solo si hay token
if (API_TOKEN) {
    startScanner();
}