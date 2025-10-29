const API_BASE_URL = 'http://comedor.mercal.gob.ve/api/p1/pedidos/takeOrder'; 
const API_CONSUMO_URL = 'http://comedor.mercal.gob.ve/api/p1/pedidos/consumo'; 

// ------------------------------------------------------------------
// ## Inicialización y Token
const bodyElement = document.getElementById('page-body');

const API_TOKEN = bodyElement ? bodyElement.dataset.apiToken : null;
const resultElement = document.getElementById('result'); // Asegúrate de que este elemento exista
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
        resultElement.innerHTML = `<p class="text-red-500">Error al escanear: ${error}</p>`;
    }
}

// ------------------------------------------------------------------
// ## Funciones de API

/**
 * Realiza una solicitud GET para obtener información usando el ID del QR (Order ID).
 * @typedef {Object} orderData
 * @returns {Promise<object|null>} Los datos del recurso o null si hay un error.
 */
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
        Swal.fire(`No se pudo actualizar el recurso  ${error.message}`);
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
            const resourceInfo = await getResourceInfo(orderData);
            let titleText = `Orden: ${decodedText}`;
            
            let htmlContent = '';
            let iconType = 'question'; // Cambiado a 'question' para la confirmación
            let confirmButtonText = 'Confirmar Consumo';
            
            if (resourceInfo) {
               
                // 1. EXTRAER order_id
                const orderId = resourceInfo.order_id; 


                 titleText = `Numero de order:${orderId || decodedText}`;
                 console.log(titleText)
                 iconType = 'info';

            } else {
                // Si el GET falla o devuelve null
                htmlContent = `<p class="text-red-500">No se pudo obtener la información para el ID: ${decodedText}. Puede que no exista o haya un error de red/API.</p>`;
                iconType = 'error'; // Error más específico
                confirmButtonText = 'Reintentar Actualización (No recomendado)';
            }
            
            // 3. Mostrar SweetAlert2 para la confirmación
            const swalResult = await Swal.fire({
                //title: titleText,
                title: "hola mundo",
                // html: htmlContent,
                icon: iconType,
                showCancelButton: true,
                confirmButtonText: confirmButtonText, 
                cancelButtonText: 'Cancelar',
                draggable: true,
                allowOutsideClick: false, 
                allowEscapeKey: false
            });

            // 4. **Paso PATCH**: Ejecutar la actualización al confirmar
            if (swalResult.isConfirmed) {
                console.log("Confirmación recibida. Iniciando solicitud PATCH...");
                
               
                const patchSuccess = await patchResourceStatus(orderData);

                if (patchSuccess) {
                   
                    Swal.fire({
                        title: '¡Consumo Confirmado!',
                        text: 'El estado del recurso ha sido actualizado con éxito. Recargando...',
                        icon: 'success',
                        confirmButtonText: confirmButtonText, 
                        cancelButtonText: 'Cancelar',
                        draggable: true,
                        allowOutsideClick: false, // Forzar la elección
                    }).then(() => {
                        window.location.reload(); 
                    });
                } else {
                   
                    startScanner(); 
                }
            } else {
                
                console.log("Acción cancelada por el usuario. Reiniciando escáner.");
                Swal.fire('Cancelado', 'La operación de actualización fue cancelada.', 'info').then(() => {
                    startScanner(); 
                });
            }
        },
        onScanError
    ).catch((err) => {
        // Manejo de errores de inicio de cámara (ej. permisos)
        //console.error("Error al iniciar el escáner (cámara):", err);
        if (resultElement) {
             resultElement.innerHTML = `<p class="text-red-700 font-bold">Error al iniciar la cámara: Verifique permisos o dispositivo. Detalle: ${err}</p>`;
        }
    });
}

// Iniciar el escáner solo si hay token
if (API_TOKEN) {
    startScanner();
}