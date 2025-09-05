const empleados = JSON.parse(document.getElementById('empleados-data').textContent);

// Variables de estado para la paginación
let currentPage = 1;
let itemsPerPage = 5;
let filteredEmployees = [...empleados];

// Referencias a elementos del DOM
const tbody = document.getElementById("dataBody");
const searchInput = document.getElementById("searchInput");
const paginationControls = document.getElementById("pagination-controls");
const itemsPerPageSelect = document.getElementById("itemsPerPageSelect");

// Función principal para renderizar la tabla
function renderTable() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const employeesToShow = filteredEmployees.slice(startIndex, endIndex);

    tbody.innerHTML = '';

    if (employeesToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">No se encontraron resultados.</td></tr>';
    } else {
        employeesToShow.forEach(empleado => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="py-3 px-1 dark:text-white text-center" data-label="Nombre">${ empleado.last_name }</td>
                <td class="py-3  dark:text-white" data-label="Almuerzo Bs">
                    <input type="checkbox" name="" value="144">
                </td>
                <td class="py-3 px-1 dark:text-white" data-label="Para llevar Bs">
                   <input type="checkbox" name="" value="10">
                </td>
                <td class="py-3 px-1 dark:text-white " data-label="Cubiertos Bs">
                     <input type="checkbox" name="" value="5">
                </td>
                <td class="py-3 px-1 dark:text-green-500 text-center" data-label="total a pagar">
                    <span id="total">0</span>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
    
    updatePaginationControls();
}

// Función para actualizar los controles de paginación
function updatePaginationControls() {
    const totalPages = Math.ceil(filteredEmployees.length / itemsPerPage);
    paginationControls.innerHTML = '';

    if (totalPages > 1) {
        // Botón "Anterior"
        const prevButton = document.createElement('button');
        prevButton.innerText = 'Anterior';
        prevButton.className = 'px-4 py-2 mr-2 bg-gray-200 rounded-md';
        prevButton.disabled = currentPage === 1;
        prevButton.addEventListener('click', () => {
            currentPage--;
            renderTable();
        });
        paginationControls.appendChild(prevButton);

        // Indicador de página actual
        const pageIndicator = document.createElement('span');
        pageIndicator.className = 'px-4 py-2';
        pageIndicator.innerText = `Página ${currentPage} de ${totalPages}`;
        paginationControls.appendChild(pageIndicator);
        
        // Botón "Siguiente"
        const nextButton = document.createElement('button');
        nextButton.innerText = 'Siguiente';
        nextButton.className = 'px-4 py-2 ml-2 bg-gray-200 rounded-md'; // Corregido: 'justify-end' fue eliminado de aquí
        nextButton.disabled = currentPage === totalPages;
        nextButton.addEventListener('click', () => {
            currentPage++;
            renderTable();
        });
        paginationControls.appendChild(nextButton);
    }
}

// Función para manejar el filtrado
function handleFilter() {
    const filter = searchInput.value.toUpperCase();
    
    filteredEmployees = empleados.filter(empleado => {
        for (const key in empleado) {
            const valor = String(empleado[key]);
            if (valor.toUpperCase().includes(filter)) {
                return true;
            }
        }
        return false;
    });

    currentPage = 1;
    renderTable();
}

// Nuevo: Escuchar los cambios en el menú desplegable de cantidad de registros
itemsPerPageSelect.addEventListener("change", (event) => {
    itemsPerPage = Number(event.target.value);
    currentPage = 1;
    renderTable();
});

// Asignar los eventos una sola vez al cargar el documento
document.addEventListener('DOMContentLoaded', () => {
    renderTable();
    searchInput.addEventListener("input", handleFilter);
});