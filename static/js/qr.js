function onScanError(error) {
    // Manejar errores de escaneo
    console.error('Error al escanear el QR: ', error);
    // Opcional: mostrar un mensaje de error al usuario
    document.getElementById('result').innerHTML = `<p class="text-red-500">Error al escanear: ${error}</p>`;
}

const html5QrCode = new Html5Qrcode("reader");

html5QrCode.start(
    { facingMode: "environment" }, // Opciones para usar la cámara trasera
    { fps: 10, qrbox: 250 },       // Opciones de escaneo
    (decodedText, decodedResult) => {
        // Callback para cuando el escaneo es exitoso
        
        // 1. Obtener la referencia al elemento 'result'
        const resultDiv = document.getElementById('result');
        
        // 2. Mostrar el texto decodificado en el HTML
        resultDiv.innerHTML = `<p class="text-green-600 font-bold">¡Código QR escaneado con éxito!</p>
                               <p class="mt-2 dark:text-white">Información: <strong>${decodedText}</strong></p>`;

        console.log(`Código escaneado: ${decodedText}`);

        // 3. Detener el escáner si solo necesitas un resultado
        html5QrCode.stop().then(() => {
            console.log("Escáner detenido.");
            // Opcional: después de detener, podrías querer hacer algo más,
            // como redirigir o enviar el dato al servidor.
        }).catch(stopErr => {
            console.error("Error al detener el escáner:", stopErr);
        });
    },
    // Nota: El callback de error individual se puede omitir si el 'catch' inicial es suficiente
    // (error) => {
    //     console.warn(`Error al escanear: ${error}`);
    // }
).catch((err) => {
    // Este `catch` maneja los errores iniciales, como la falta de permisos.
    console.error("Error al iniciar el escáner:", err);
    // Mostrar error de inicio al usuario
    document.getElementById('result').innerHTML = `<p class="text-red-700 font-bold">Error al iniciar la cámara: ${err}</p>`;
});