// Función para alternar entre modo claro y oscuro
function toggleDarkMode() {
    document.documentElement.classList.toggle('dark');
    // **Guarda el estado actual del modo oscuro ('true' o 'false')**
    localStorage.setItem('darkMode', document.documentElement.classList.contains('dark').toString());
}

// Obtener la preferencia guardada
const storedDarkMode = localStorage.getItem('darkMode');

// Comprobar preferencias del usuario al cargar la página
if (storedDarkMode === 'true') {
    // Si la preferencia guardada es 'true', aplica el modo oscuro
    document.documentElement.classList.add('dark');
} else if (storedDarkMode === 'false') {
    // Si la preferencia guardada es 'false', asegúrate de que no tenga el modo oscuro (modo claro)
    document.documentElement.classList.remove('dark');
} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    // **SOLO si NO hay preferencia guardada (primera visita),**
    // comprueba la preferencia del sistema y aplica si es oscuro
    document.documentElement.classList.add('dark');
}

