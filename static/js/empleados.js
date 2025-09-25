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
                    lunch: 'No',
                    to_go: 'No',
                    covered: 'No'
                };
            }
            employeeSelections[employeeIndex][selectionType] = isChecked ? 'Si' : 'No';
        }
    });

   

    // --- 4. Renderizado Inicial ---
    renderTable();
});
