document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Variables y Elementos del DOM ---
    const table = document.getElementById('myTable');
    const tbody = table.querySelector('tbody');
    const searchInput = document.getElementById('searchInput');
    const rowsPerPageSelect = document.getElementById('rowsPerPage');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const pageNumbersSpan = document.getElementById('pageNumbers');
    const resumenForm = document.getElementById('resumen-form');

    const allRows = Array.from(tbody.querySelectorAll('tr'));
    let filteredRows = [...allRows];
    let currentPage = 1;
    let rowsPerPage = parseInt(rowsPerPageSelect.value);

    // Objeto para almacenar las selecciones de todos los empleados
    const employeeSelections = {};
    console.log(employeeSelections)
    // --- 2. Funciones de Lógica de Negocio ---
    function renderTable() {
        tbody.innerHTML = '';
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const paginatedRows = filteredRows.slice(start, end);

        if (paginatedRows.length === 0) {
            const noResultsRow = document.createElement('tr');
            noResultsRow.innerHTML = `<td colspan="${table.querySelectorAll('th').length}" style="text-align: center; padding: 20px;">No se encontraron resultados.</td>`;
            tbody.appendChild(noResultsRow);
        } else {
            paginatedRows.forEach(row => {
                const employeeIndex = row.dataset.employeeIndex;
                const selections = employeeSelections[employeeIndex] || {};

                // Restaurar estado de checkboxes si existen
                const lunchCheckbox = row.querySelector(`[name="lunch_${employeeIndex}"]`);
                const toGoCheckbox = row.querySelector(`[name="to_go_${employeeIndex}"]`);
                const coveredCheckbox = row.querySelector(`[name="covered_${employeeIndex}"]`);

                if (lunchCheckbox) lunchCheckbox.checked = selections.lunch === 'Si';
                if (toGoCheckbox) toGoCheckbox.checked = selections.to_go === 'Si';
                if (coveredCheckbox) coveredCheckbox.checked = selections.covered === 'Si';

                tbody.appendChild(row);
            });
        }
        updatePaginationControls();
    }

    function updatePaginationControls() {
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
        pageNumbersSpan.textContent = `Página ${currentPage} de ${totalPages}`;
        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages || totalPages === 0;
    }

    function handleSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        if (searchTerm === '') {
            filteredRows = [...allRows];
        } else {
            filteredRows = allRows.filter(row => {
                return Array.from(row.children).some(cell =>
                    cell.textContent.toLowerCase().includes(searchTerm)
                );
            });
        }
        currentPage = 1;
        renderTable();
    }

    function handleRowsPerPageChange() {
        rowsPerPage = parseInt(rowsPerPageSelect.value);
        currentPage = 1;
        renderTable();
    }

    function handlePrevClick() {
        if (currentPage > 1) {
            currentPage--;
            renderTable();
        }
    }

    function handleNextClick() {
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderTable();
        }
    }
    
    // --- 3. Event Listeners ---
    searchInput.addEventListener('input', handleSearch);
    rowsPerPageSelect.addEventListener('change', handleRowsPerPageChange);
    prevBtn.addEventListener('click', handlePrevClick);
    nextBtn.addEventListener('click', handleNextClick);

    // Listener para capturar cambios en los checkboxes
   tbody.addEventListener('change', (event) => {
        if (event.target.type === 'checkbox') {
            const row = event.target.closest('tr');
            if (!row) return; // Protección por si no encuentra fila
            const employeeIndex = row.dataset.employeeIndex;
            const selectionType = event.target.dataset.selectionType;
            if (!employeeIndex || !selectionType) return; // Protección

            const isChecked = event.target.checked;

            if (!employeeSelections[employeeIndex]) {
                employeeSelections[employeeIndex] = {
                    index: employeeIndex,
                    name: row.dataset.employeeName,
                    
                    // --- CAPTURAR LA CÉDULA DE LA FILA ---
                    cedula: row.dataset.employeeCedula,
                    
                    
                    lunch: 'No',
                    to_go: 'No',
                    covered: 'No'
                };
            }
            employeeSelections[employeeIndex][selectionType] = isChecked ? 'Si' : 'No';
            console.log(employeeSelections);
        }
    });

    // Listener para el envío del formulario
    resumenForm.addEventListener('submit', (event) => {
        // Si quieres evitar el envío real, descomenta la siguiente línea:
        // event.preventDefault();

        // Eliminar inputs ocultos previos
            const oldInputs = resumenForm.querySelectorAll('input[name^="employees_"], input[name^="lunch_"], input[name^="to_go_"], input[name^="covered_"], input[name^="cedula_"], input[name="total_employees"]');

        oldInputs.forEach(input => input.remove());

        let employeeCount = 0;
        for (const index in employeeSelections) {
            const selection = employeeSelections[index];
            
            if (selection.lunch === 'Si' || selection.to_go === 'Si' || selection.covered === 'Si') {
               
                const inputCedula = document.createElement('input');
                inputCedula.type = 'hidden';
                inputCedula.name = `cedula_${index}`;
                inputCedula.value = selection.cedula; // Usar el valor almacenado
                resumenForm.appendChild(inputCedula);

                const inputName = document.createElement('input');
                inputName.type = 'hidden';
                inputName.name = `employees_${index}`;
                inputName.value = selection.name;
                resumenForm.appendChild(inputName);

                const inputLunch = document.createElement('input');
                inputLunch.type = 'hidden';
                inputLunch.name = `lunch_${index}`;
                inputLunch.value = selection.lunch;
                resumenForm.appendChild(inputLunch);

                const inputToGo = document.createElement('input');
                inputToGo.type = 'hidden';
                inputToGo.name = `to_go_${index}`;
                inputToGo.value = selection.to_go;
                resumenForm.appendChild(inputToGo);

                const inputCovered = document.createElement('input');
                inputCovered.type = 'hidden';
                inputCovered.name = `covered_${index}`;
                inputCovered.value = selection.covered;
                resumenForm.appendChild(inputCovered);

                employeeCount++;
            }
        }
        
        const totalInput = document.createElement('input');
        totalInput.type = 'hidden';
        totalInput.name = 'total_employees';
        totalInput.value = employeeCount;
        resumenForm.appendChild(totalInput);
    });

    // --- 4. Renderizado Inicial ---
    renderTable();
});
