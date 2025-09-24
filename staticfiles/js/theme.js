
        // Función para alternar entre modo claro y oscuro
        function toggleDarkMode() {
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
        }

        // Comprobar preferencias del usuario al cargar la página
        if (localStorage.getItem('darkMode') === 'true' || 
            (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
        }


               tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        dark: {
                            100: '#1E293B',
                            200: '#0F172A',
                        }
                    }
                }
            }
        }