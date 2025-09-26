function onScanError(error) {
    // Manejar errores de escaneo
    console.error('Error al escanear el QR: ', error);
    // Opcional: mostrar un mensaje de error al usuario
    document.getElementById('result').innerHTML = `<p class="text-red-500">Error al escanear: ${error}</p>`;
}

const html5QrCode = new Html5Qrcode("reader");

html5QrCode.start(
    { facingMode: "environment" }, 
    { fps: 10, qrbox: 250 },
    (decodedText, decodedResult) => {
              
        // Obtener el elemento donde se mostrará el resultado
        const resultDiv = document.getElementById('result');
        
        //  Mostrar el texto decodificado en el HTML
            Swal.fire({
            title: decodedText,
            icon: "success",
            draggable: true
            }).then((result) => {
                // Esta función se ejecuta cuando la ventana se cierra (con o sin botón)
                if (result.isConfirmed || result.dismiss === Swal.DismissReason.backdrop || result.dismiss === Swal.DismissReason.close) {
                    // Recarga la página actual
                    window.location.reload(); 
                }
            });

        // resultDiv.innerHTML = `<p class="mt-2 dark:text-white flex flex-col"><strong></strong></p>`;

        console.log(`Código escaneado: ${decodedText}`);

        // Detener el escáner si solo necesitas un resultado
        html5QrCode.stop().then(() => {
            console.log("Escáner detenido.");
        
        }).catch(stopErr => {
            console.error("Error al detener el escáner:", stopErr);
        });
    },
   
).catch((err) => {
   
    console.error("Error al iniciar el escáner:", err);
   
    document.getElementById('result').innerHTML = `<p class="text-red-700 font-bold">Error al iniciar la cámara: ${err}</p>`;
});