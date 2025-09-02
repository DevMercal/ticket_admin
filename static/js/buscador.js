 function filterTable() {
            // 1. Declarar variables
            let input, filter, table, tr, td, i, txtValue;
            input = document.getElementById("searchInput");
            filter = input.value.toUpperCase(); // Convertir el texto a mayúsculas para que la búsqueda no distinga entre mayúsculas y minúsculas
            table = document.getElementById("dataTable");
            tr = table.getElementsByTagName("tr");

            // 2. Iterar sobre todas las filas de la tabla y ocultar las que no coincidan
            for (i = 0; i < tr.length; i++) {
                // La búsqueda se realiza en la primera celda (nombre) pero puedes modificar esto
                td = tr[i].getElementsByTagName("td")[0]; 
                if (td) {
                txtValue = td.textContent || td.innerText; // Obtener el texto de la celda
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = ""; // Mostrar la fila si coincide
                } else {
                    tr[i].style.display = "none"; // Ocultar la fila si no coincide
                }
                }
            }
            }