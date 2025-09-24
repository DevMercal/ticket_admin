// Obtener los elementos del DOM
const openModalBtn = document.getElementById('openModalBtn');
const modal = document.getElementById('myModal');
const closeButtons = document.querySelectorAll('[data-dismiss="modal"]');

// Función para mostrar el modal
function showModal() {
    modal.classList.add('show');
}

// Función para ocultar el modal
function hideModal() {
    modal.classList.remove('show');
}

// Event listener para abrir el modal
openModalBtn.addEventListener('click', showModal);

// Event listeners para cerrar el modal (botones con data-dismiss)
closeButtons.forEach(button => {
    button.addEventListener('click', hideModal);
});

// Event listener para cerrar el modal al hacer clic en el fondo
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        hideModal();
    }
});
