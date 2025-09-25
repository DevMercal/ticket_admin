function onScanSuccess(decodedText, decodedResult) {
            // Manejar el resultado del escaneo aquí
            document.getElementById('result').innerText = `Código QR: ${decodedText}`;
            // Puedes enviar `decodedText` a tu vista de Django para procesarlo
            console.log(`Código QR escaneado: ${decodedText}`, decodedResult);
            // Para enviar a Django, puedes usar una llamada AJAX o un formulario
        }

        function onScanError(error) {
            // Manejar errores de escaneo
            console.error('Error al escanear el QR: ', error);
        }

       const html5QrCode = new Html5Qrcode("reader");

        html5QrCode.start(
            { facingMode: "environment" }, // Opciones para usar la cámara trasera
            { fps: 10, qrbox: 250 },       // Opciones de escaneo
            (decodedText, decodedResult) => {
                // Callback para cuando el escaneo es exitoso
                console.log(`Código escaneado: ${decodedText}`);
                // Detener el escáner si solo necesitas un resultado
                html5QrCode.stop().then(() => {
                    console.log("Escáner detenido.");
                });
            },
            // (error) => {
            //     // Callback para manejar errores
            //     console.warn(`Error al escanear: ${error}`);
            // }
        ).catch((err) => {
            // Este `catch` maneja los errores iniciales, como la falta de permisos.
            console.error("Error al iniciar el escáner:", err);
        });