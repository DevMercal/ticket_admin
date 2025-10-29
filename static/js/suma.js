// 1. Obtener todos los checkboxes relevantes
// Usamos la clase 'selection-checkbox' que añadimos en el HTML
const checkboxes = document.querySelectorAll('.selection-checkbox');
const totalInput = document.getElementById('total');


/**
 * Calcula el total sumando los valores de los checkboxes seleccionados.
 */
function calculateTotal() {
    let total = 0; 
// Iterar sobre todos los checkboxes
    checkboxes.forEach(checkbox => {
        // Verificar si el checkbox está marcado (checked)
        if (checkbox.checked) {
            // Si está marcado, sumar su valor.
            // Es importante usar parseFloat() o parseInt() para sumar números.
            // Si no está marcado, su valor no se suma.
            total += parseFloat(checkbox.value) || 0; // || 0 previene errores si el valor no es un número
            
        }
    });
    console.log("Total calculado (antes de mostrar):", total);
    // Mostrar el resultado en el campo 'total'
    totalInput.value = total.toFixed(2); // toFixed(2) para mostrar dos decimales
    console.log("Total calculado:", totalInput.value);
    // Opcional: También puedes mostrarlo en la consola si lo necesitas
    console.log("Nuevo Total:", total.toFixed(2));
}

// 2. Asignar la función a los eventos
// Añadir un 'event listener' a cada checkbox
checkboxes.forEach(checkbox => {
    // Cada vez que se haga clic (cambie de estado) en un checkbox,
    // se ejecutará la función 'calculateTotal'.
    checkbox.addEventListener('change', calculateTotal);
});

// Opcional: Ejecutar el cálculo al cargar la página si ya hay alguno marcado
calculateTotal();