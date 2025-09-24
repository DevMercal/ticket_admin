// Función principal que genera los grupos de input
function generarGrupoMenu(titulo, btnId, containerId, inputName) {
    const contenedorPrincipal = document.getElementById('container-grupos-menu');
    
    // Crear un contenedor para cada grupo (título, input principal y inputs agregados)
    const grupoContenedor = document.createElement('div');
    // Le agregamos un estilo para cada grupo
    grupoContenedor.className = 'flex flex-col flex-1';

    // Crear el título del grupo
    const tituloElemento = document.createElement('h5');
    tituloElemento.textContent = titulo;
    tituloElemento.className = 'text-lg font-semibold dark:text-white mt-4 capitalize';

    // Crear el div para el input principal y el botón
    const divMain = document.createElement('div');
    divMain.className = 'flex gap-2 p-2';

    const mainInput = document.createElement('input');
    mainInput.type = 'text';
    mainInput.className = 'dark:bg-gray-800 border border-blue-600 py-1 px-4 rounded-lg flex-1';
    mainInput.name = inputName; // Asignamos el nombre al input principal

    const btnAgregar = document.createElement('button');
    btnAgregar.type = 'button';
    btnAgregar.textContent = '+';
    btnAgregar.id = btnId; // Asignar el ID al botón para el evento
    btnAgregar.className = 'border border-blue-600 rounded-md px-2';

    divMain.appendChild(mainInput);
    divMain.appendChild(btnAgregar);

    // Crear el div para los inputs agregados dinámicamente
    const divInputsAgregados = document.createElement('div');
    divInputsAgregados.id = containerId; // Asignar el ID al contenedor
    divInputsAgregados.className = 'flex flex-col px-3';
    
    // Añadir todos los elementos al contenedor del grupo
    grupoContenedor.appendChild(tituloElemento);
    grupoContenedor.appendChild(divMain);
    grupoContenedor.appendChild(divInputsAgregados);
    
    // Añadir el contenedor del grupo al contenedor principal del formulario
    contenedorPrincipal.appendChild(grupoContenedor);
    
    // Configurar la lógica para agregar inputs al contenedor secundario
    agregarInputDinamico(btnId, containerId, mainInput, inputName);
}

// Función reutilizable para añadir inputs (ahora recibe el inputName)
function agregarInputDinamico(btnId, containerId, mainInputElem, inputName) {
    const btnElem = document.getElementById(btnId);
    const itemContainer = document.getElementById(containerId);

    btnElem.addEventListener('click', e => {
        e.preventDefault();

        const inputValue = mainInputElem.value.trim();
        if (inputValue === '') {
            console.log('El campo principal no puede estar vacío.');
            return;
        }

        // Limite a 3 inputs en el contenedor secundario
        if (itemContainer.children.length >= 2) {
            console.log(`¡Se ha alcanzado el límite de 3 entradas para este grupo!`);
            return;
        }

        const nuevoInput = document.createElement('input');
        nuevoInput.type = 'text';
        nuevoInput.value = inputValue;
        nuevoInput.name = inputName; // Nombre del input igual al del grupo
        nuevoInput.className = 'border dark:bg-gray-600 py-1 px-2 rounded-md dark:text-white mb-2';

        itemContainer.appendChild(nuevoInput);

        // Limpiar el input principal
        mainInputElem.value = '';
    });
}

// Llama a la función para cada grupo de menú que necesites
// Elige IDs únicos para los botones y los contenedores y un nombre único para el input
generarGrupoMenu('sopas', 'btnAgregar_sopa', 'sopas', 'sopas');
generarGrupoMenu('proteinas', 'btnAgregar_entradas', 'proteinas', 'proteinas');
generarGrupoMenu('contornos', 'btnAgregar_principales', 'contornos', 'contornos');
generarGrupoMenu('postres', 'btnAgregar_postres', 'postres', 'postres');
generarGrupoMenu('bebidas', 'btnAgregar_bebidas', 'bebidas', 'bebidas');