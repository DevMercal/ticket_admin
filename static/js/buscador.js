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
    let rowsPerPage = parseInt(rowsPerPageSelect.value, 10); // ✅ Especificar base decimal

    const employeeSelections = {};

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
        prevBtn.disabled = currentPage <= 1;
        nextBtn.disabled = currentPage >= totalPages;
    }

    function handleSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        filteredRows = searchTerm === ''
            ? [...allRows]
            : allRows.filter(row =>
                Array.from(row.children).some(cell =>
                    cell.textContent.toLowerCase().includes(searchTerm)
                )
            );
        currentPage = 1;
        renderTable();
    }

    function handleRowsPerPageChange() {
        rowsPerPage = parseInt(rowsPerPageSelect.value, 10); // ✅ base decimal
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

    tbody.addEventListener('change', (event) => {
        if (event.target.type === 'checkbox') {
            const row = event.target.closest('tr');
            if (!row) return;

            const employeeIndex = row.dataset.employeeIndex;
            const employeeCedula = row.dataset.employeeCedula;
            const selectionType = event.target.dataset.selectionType;
            const isChecked = event.target.checked;

            if (!employeeIndex || !selectionType || !employeeCedula) return;

            if (!employeeSelections[employeeCedula]) {
                employeeSelections[employeeCedula] = {
                    name: row.dataset.employeeName,
                    cedula: employeeCedula,
                    lunch: 'No',
                    to_go: 'No',
                    covered: 'No'
                };
            }

            //Corrección: asegurar que se actualiza el objeto correcto
            employeeSelections[employeeCedula][selectionType] = isChecked ? 'Si' : 'No';
        }
    });

    resumenForm.addEventListener('submit', (event) => {
        const oldInputs = resumenForm.querySelectorAll('input[name^="employees_"], input[name^="lunch_"], input[name^="to_go_"], input[name^="covered_"], input[name^="cedula_"], input[name^="employee_index_"], input[name="total_employees"]');
        oldInputs.forEach(input => input.remove());

        let employeeCount = 0;
        let i = 0;

        for (const cedula in employeeSelections) {
            const selection = employeeSelections[cedula];
            if (selection.lunch === 'Si' || selection.to_go === 'Si' || selection.covered === 'Si') {
                const fields = {
                    [`cedula_${i}`]: selection.cedula,
                    [`employees_${i}`]: selection.name,
                    [`employee_index_${i}`]: cedula,
                    [`lunch_${i}`]: selection.lunch,
                    [`to_go_${i}`]: selection.to_go,
                    [`covered_${i}`]: selection.covered
                };

                for (const [name, value] of Object.entries(fields)) {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = name;
                    input.value = value;
                    resumenForm.appendChild(input);
                }

                i++;
                employeeCount++;
            }
        }

        const totalInput = document.createElement('input');
        totalInput.type = 'hidden';
        totalInput.name = 'total_employees';
        totalInput.value = employeeCount;
        resumenForm.appendChild(totalInput);
    });

    
    renderTable();
});
