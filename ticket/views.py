from PIL import Image
from requests.exceptions import ConnectionError, HTTPError, Timeout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import  logout
from django.contrib import messages
import requests
import qrcode
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from django.conf import settings
import matplotlib.patches as mpatches
import os
import mimetypes
import json
LOGO_PATH = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png')

api_url = settings.API

def inicio(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
 
        data = {
            'email': email,
            'password': password
        }

        try:
            
            response = requests.post(f"{api_url}/users/login", json=data)
            
            if response.status_code == 200:
                json_data = response.json()
                empleados = json_data.get('data', [])
                
                token = json_data.get('token')
                name = empleados.get('name')
                email = empleados.get('email')
                
                if token:
                    
                    request.session['api_token'] = token
                    request.session['name'] = name
                    request.session['email'] = email
                    
                    messages.success(request, '¡Inicio de sesión exitoso!')
                    
                    return redirect('index')
                else:
                    messages.error(request, 'Token no encontrado en la respuesta de la API.')
            else:
             
                messages.error(request, 'Credenciales incorrectas. Por favor, inténtelo de nuevo.')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error de conexión con la API: {e}')

    return render(request, 'paginas/login.html')

def progreso_mensual_view(request):
    """
    Genera el gráfico de progreso mensual con Matplotlib
    y lo devuelve como una imagen PNG.
    """
    # Los datos pueden ser dinámicos, por ejemplo, de un modelo de Django
    completado = 70
    restante = 100 - completado

    # Colores y etiquetas
    colores = ['#6a5acd', '#464860']
    etiquetas = ['Completado', 'Restante']

    # Crear el gráfico de tarta (estilo donut)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie([completado, restante],
           colors=colores,
           startangle=90,
           wedgeprops={'edgecolor': '#282c34', 'width': 0.3})

    # Añadir el texto en el centro
    ax.text(0, 0, f'{completado}%',
            ha='center', va='center',
            fontsize=40, color='white', weight='bold')
    ax.text(0, -0.2, 'Objetivo',
            ha='center', va='center',
            fontsize=20, color='white')

    # Crear la leyenda
    legend_elements = [
        mpatches.Patch(facecolor=colores[0], label=f'{etiquetas[0]}   {completado}%'),
        mpatches.Patch(facecolor=colores[1], label=f'{etiquetas[1]}   {restante}%')
    ]
    ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.1),
              ncol=1, frameon=False, fontsize=12, labelcolor='white')

    # Configurar el fondo y el título
    fig.patch.set_facecolor('#282c34')
    ax.set_facecolor('#282c34')
    ax.set_title('Progreso Mensual', fontsize=20, color='white', weight='bold')
    ax.axis('equal')

    # Guardar el gráfico en un buffer en memoria en lugar de un archivo
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', transparent=True)
    buffer.seek(0)
    plt.close(fig) # Cierra la figura para liberar memoria

    # Devolver la imagen como una respuesta HTTP
    return HttpResponse(buffer.getvalue(), content_type='image/png') 

def index(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio')  
    
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f"{api_url}/users", headers=headers, timeout=10)
        response.raise_for_status() 
        json_data = response.json()
        user = json_data.get('data', [])
        number = len(user)
        
    except (ConnectionError, HTTPError, Timeout) as e:
        print(f"Error al conectar con la API: {e}")
        number = 0
        json_data = []
    contexto = {
        'number': number,
        'datos_usuarios': json_data,  
        'current_page': 'dashboard'
    }
    
    return render(request, 'paginas/index.html', contexto)

def usu(request: HttpRequest):
   
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio')  
    
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
      
      
    try:
     
        response = requests.get(f"{api_url}/users", headers=headers, timeout=10)
        
        
        response.raise_for_status() 
        
       
        json_data = response.json()
       
        usuarios = json_data.get('data', [])
        
        
   
    except requests.exceptions.ConnectionError as conn_err:
        messages.error(request, f"Error de conexión: {conn_err} - No se pudo conectar con la API.")
            
    except requests.exceptions.Timeout as timeout_err:
        messages.error(request, f"Error de tiempo de espera: {timeout_err} - La solicitud tardó demasiado en responder.")
            
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error inesperado: {req_err}")

    result = {
        'usuarios' : usuarios,
        'current_page' : 'usuarios'
    }    
    
    return render(request, 'paginas/usuarios.html', result)

def user_registro(request: HttpRequest) -> HttpResponse:
 
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    if request.method == 'POST': 
       
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password_confirmation = request.POST.get('password_confirmation', '')
        id_management = request.POST.get('id_management', '')

       
        if not all([name, email, password, password_confirmation, id_management]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('usu') 

        data = {
            'name': name,
            'email': email,
            'password': password,
            'password_confirmation': password_confirmation,
            'id_management': id_management
        }

        try:
            
            response = requests.post(f"{api_url}/users", json=data, headers=headers, timeout=10)
            response.raise_for_status()  # This will raise an HTTPError for 4xx/5xx status codes

            messages.success(request, 'Usuario registrado exitosamente.')
            return redirect('usu')

        except requests.exceptions.HTTPError as e:
            # Handle HTTP-specific errors (e.g., 400 Bad Request, 401 Unauthorized)
            try:
                json_data = response.json()
                error_message = json_data.get('message', 'Error al registrar el usuario.')
                messages.error(request, error_message)
            except requests.exceptions.JSONDecodeError:
                # Handle cases where the response isn't valid JSON
                messages.error(request, f'Error del servidor: {response.text}')

        except requests.exceptions.RequestException as e:
            # Catch all other request-related errors (e.g., connection, DNS)
            messages.error(request, f'Error de conexión con la API: {e}')

    return render(request, 'paginas/usuarios.html') # Replace with your form template path

def eliminar_user(request, id):
    if request.method == 'GET':
      
        token = request.session.get('api_token')
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.delete(f"{api_url}/users/{id}", headers=headers, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses

            messages.success(request, 'Usuario eliminado exitosamente.')
            return redirect('usu')

        except requests.exceptions.HTTPError as e:
            try:
                json_data = response.json()
                error_message = json_data.get('message', 'Error al eliminar el usuario.')
                messages.error(request, error_message)
            except requests.exceptions.JSONDecodeError:
                messages.error(request, f'Error del servidor: {response.text}')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error de conexión con la API: {e}')

    return redirect('usu')

def actulizar_menu(request, date_menu):
    pass
          
def registro_menu(request):
    if request.method == 'POST':
        
        sopas = request.POST.getlist('sopas')
        contornos = request.POST.getlist('contornos')
        proteinas = request.POST.getlist('proteinas')
        postres = request.POST.getlist('postres') 
        bebidas = request.POST.getlist('bebidas')
        
       
        data = []
        
        
        def agregar_al_payload(categoria, ingredientes):
            if ingredientes:
                
                ingredient_string = ", ".join(ingredientes)
                data.append({
                    "foodCategory": categoria,
                    "ingredient": ingredient_string
                })
        
      
        agregar_al_payload("Sopas", sopas)
        agregar_al_payload("Contornos", contornos)
        agregar_al_payload("Proteinas", proteinas)
        agregar_al_payload("Postres", postres)
        agregar_al_payload("Bebidas", bebidas)
        
        try:
            token = request.session.get('api_token')
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            response = requests.post(f"{api_url}/menus/bluk", json=data, headers=headers, timeout=10)
            response.raise_for_status() 

            messages.success(request, 'Menú registrado exitosamente.')
            return redirect('menu')

        except requests.exceptions.RequestException as e:
            # Manejar errores de la solicitud (conexión, timeouts, etc.)
            messages.error(request, f"Error al registrar: {e}")
        except Exception as e:
            # Manejar otros errores inesperados
            messages.error(request, f"Ocurrió un error inesperado: {e}")

    # Renderiza la plantilla si el método no es POST
    return render(request, 'paginas/menu.html')

def menu(request):
    
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio')

    
    menus = []
    date_of_menu = None 
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
   
    
    try:
        response = requests.get(f"{api_url}/menus", headers=headers, timeout=10)
        response.raise_for_status() 
        
        json_data = response.json()
        
        try:
            menus = json_data.get('menus', [])
            menu_item = menus[4]

            
            date_of_menu = menu_item['date_menu']
        except Exception as e:
            messages.error(request, "No hay registro de menu")       
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error inesperado: {req_err}")
    contexto= {
        'date_of_menu':date_of_menu,
        'menus': menus,
        'current_page' : 'menu'
    }
   
    return render(request, 'paginas/menu.html', contexto)

def seleccion(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect(inicio)

    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    selected_management = request.GET.get('management', '')
    
    params = {'gerencias': selected_management} if selected_management else {}
    
    employees = []
    processed_employees = []
    management = []
    try:
            response = requests.get(f"{api_url}/empleados", headers=headers, params=params, timeout=10)
            response.raise_for_status()
            json_data = response.json()
            
            
            employees = json_data.get('employees', [])
            
            
            # Iterate over each employee in the list
            for names_lasname in employees:
                full_first_name = names_lasname.get("first_name")
                full_last_name = names_lasname.get("last_name")
                
                # Safely split and concatenate the names
                first_name = full_first_name.split()[0] if full_first_name else ""
                first_last_name = full_last_name.split()[0] if full_last_name else ""
                
                # Combine into a full name
                full_name = f"{first_name} {first_last_name}".strip()
                
                # Add the full name to the current employee's dictionary
                names_lasname['full_name'] = full_name
                
                # Append the processed employee data to the new list
                processed_employees.append(names_lasname)
       
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error al obtener empleados: {req_err}")

    try:
        response_management = requests.get(f"{api_url}/gerencias", headers=headers, timeout=10)
        response_management.raise_for_status()
        json_management = response_management.json()
        
        management = json_management.get('management', [])   
        
    except requests.exceptions.RequestException as req_err:
        messages.warning(request, f"No se pudo cargar la lista de gerencias: {req_err}")
    return render(request, 'paginas/seleccion.html', {
        'management': management,
        'selected_management': selected_management,
        'employees': processed_employees, 
        'current_page' : 'seleccion'})

def resumen(request):
    if request.method == 'POST':
        total = int(request.POST.get('total_employees', 0))
        
        total_pago_general = request.POST.get('total_pago_general', '0.00')
        
        resumen_empleados = []
        
        
        for i in range(total): 
           
            employee_name = request.POST.get(f'employees_{i}') 
            employee_index = request.POST.get(f'employee_index_{i}')
            cedula = request.POST.get(f'cedula_{i}')
            
            if not employee_name:
                continue 
            
            
            lunch = request.POST.get(f'lunch_{i}', 'No')
            to_go = request.POST.get(f'to_go_{i}', 'No')
            covered = request.POST.get(f'covered_{i}', 'No')
           
            
            if lunch == 'No' and to_go == 'No' and covered == 'No':
                continue

            resumen_empleados.append({
                'employees': employee_name,
                'lunch': lunch,
                'to_go': to_go,
                'covered': covered,
                'cedula': cedula,
            })
            
            
        if resumen_empleados:
            request.session['resumen_empleados'] = resumen_empleados
            contexto = {
                'contexto': resumen_empleados,
                'current_page': 'resumen',
                'total_general': total_pago_general 
            }
                
            return render(request, 'paginas/resumen.html', contexto)
    
    messages.warning(request, "Acceso denegado: Debe seleccionar un empleado para acceder a esta vista.")
    return redirect('seleccion')

def registration_order(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') # Asumiendo el nombre de la URL 'inicio'

    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    # La variable 'resumen_empleados' no se usa en el bloque POST, pero la mantengo si tiene un propósito en el GET
    resumen_empleados = request.session.get('resumen_empleados', []) 

    if request.method == 'POST':
        # 1. Recuperar y CONVERTIR/PREPARAR los datos
        
        # --- CAMPOS STRING ---
        special_event = request.POST.get('special_event', 'No')
        authorized = request.POST.get('authorized', 'No')      
        authorized_person = request.POST.get('authorized_person', '')
        total_amount = request.POST.get('total_amount', '0.0') # 'required|string'

        # --- CAMPOS NUMÉRICOS (Convertidos a STRING para el envío 'multipart') ---
        try:
            # reference: 'required|numeric'
            reference = str(float(request.POST.get('reference') or 0.0))
        except ValueError:
            messages.error(request, " Error: El campo 'Referencia' debe ser numérico.")
            return redirect('pedidos')
            
        try:
            # cedula: 'required|numeric'
            cedula = str(int(request.POST.get('cedula') or 0))
        except ValueError:
            messages.error(request, " Error: El campo 'Cédula de la Orden' debe ser un número entero.")
            return redirect('pedidos')

        try:
            # IDs: Convertidos a STRING
            id_payment_method = str(int(request.POST.get('id_payment_method') or 0))
            id_order_status = str(int(request.POST.get('id_order_status', '1')))
            id_orders_consumption = str(int(request.POST.get('id_orders_consumption', '1')))
        except ValueError:
            messages.error(request, " Error: Los IDs de pago o estado deben ser números enteros.")
            return redirect('pedidos')
            
        # --- Campos de EmployeePayment (STRING) ---
        cedula_employee = request.POST.get('cedula_employee')
        name_employee = request.POST.get('name_employee')
        phone_employee = request.POST.get('phone_employee', '')
        management = request.POST.get('management') 
        extras = request.POST.get('extras', '1') 
        
        payment_support = request.FILES.get('payment_support')
        
        
        # 2. Construir el JSON y el Payload
        data_for_json = {
                "order": {
                    'special_event': special_event,
                    'authorized': authorized,
                    'id_payment_method': id_payment_method,
                    'id_order_status':id_order_status,
                    'authorized_person': authorized_person,
                    'reference':reference,
                    'cedula': cedula, 
                    'total_amount':total_amount,
                    'id_orders_consumption': str(id_orders_consumption),
                },
                "employeePayment": {
                    'cedula_employee': cedula_employee,
                    'name_employee': name_employee,
                    'phone_employee':phone_employee,
                    'management': management,
                },
                # Los arrays simples a menudo van como listas JSON
                "extras": [extras] 
            }

        orders = [data_for_json]
        orders_json_string = json.dumps(orders)
        payload_data = {
            'orders_json':  orders_json_string
        }
        print(payload_data) # Eliminado para limpieza

        # 3. Preparar los archivos
        files_to_send = {}
        if payment_support:
            content_type = mimetypes.guess_type(payment_support.name)[0] or 'application/octet-stream'

            files_to_send = [
                # Tupla: (nombre_campo, (nombre_archivo, datos_archivo, tipo_mime))
                ('payment_supports[]', (payment_support.name, payment_support.file, content_type))
            ]
        
        # 4. Enviar la solicitud a la API
        try:
            # Aquí es donde estaba la indentación INCORRECTA
            # El bloque de código de la petición debe estar DENTRO del 'if request.method == 'POST':'
            # y NO anidado en una estructura incorrecta.
            
            response = requests.post(
                f"{api_url}/pedidos/bluk", 
                headers=headers, 
                data=payload_data, 
                files=files_to_send, 
                timeout=10
            )
                    
            # print(response) # Eliminado para limpieza
            # print(f"Código de estado de la respuesta: {response.status_code}") # Eliminado para limpieza

            # 5. Manejo de la Respuesta de la API
            
            # Intenta obtener el JSON de la respuesta para la depuración y el éxito
            try:
                response_json = response.json()
                # print(response_json) # Eliminado para limpieza
            except requests.exceptions.JSONDecodeError:
                # print("La respuesta no contiene JSON válido. Contenido de la respuesta:") # Eliminado para limpieza
                # print(response.text) # Eliminado para limpieza
                # Si la respuesta no es 2xx y no tiene JSON, raise_for_status lo manejará.
                pass 
           
            
            response.raise_for_status() # Esto lanzará una excepción HTTPError para respuestas 4xx/5xx
            
            # Si llegamos aquí, la respuesta fue 2xx
            request.session['order_data_for_ticket'] = response.json()
            messages.success(request, "La orden se ha registrado correctamente. ")
            return redirect('ticket')

        except requests.exceptions.HTTPError as err:
            # print(f"Error {response.status_code} - Respuesta de la API: {response.text}") # Eliminado para limpieza
            
            error_msg = f"Error: {response.status_code}. Detalles no disponibles."
            try:
                error_data = response.json()
                # Mostrar el detalle del error de validación
                error_msg = error_data.get('message', error_msg)
                
                if 'errors' in error_data:
                    validation_errors = [f"{k}: {', '.join(v)}" for k, v in error_data['errors'].items()]
                    error_msg += " | Detalles: " + " | ".join(validation_errors)

            except:
                # Si falla la decodificación del JSON del error, usamos el mensaje genérico
                pass 
            messages.error(request, f" Error al registrar: {error_msg}")

        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexión con la API de órdenes.")
            # print(f"Error de conexión: {e}") # Eliminado para limpieza

    # Renderiza la plantilla si no es un POST o si hay un error antes de la redirección
    # o si se ejecuta la primera vez (método GET)
    return render(request, "paginas/pedidos.html")

def ticket(request):
    
    if request.method != 'GET':
        messages.warning(request, "Acceso no válido.")
        return redirect('seleccion')
        
    #PASO CLAVE 1: Recuperar los datos de la sesión
    resumen_empleados = request.session.get('resumen_empleados', [])
    order_data = request.session.get('order_data_for_ticket', {})
    
    # Si no hay empleados, no hay tiques que generar
    if not resumen_empleados:
        messages.warning(request, "No hay empleados registrados para generar ticket.")
        # Limpiamos la sesión si es necesario antes de redirigir
        if 'order_data_for_ticket' in request.session:
             del request.session['order_data_for_ticket']
        return redirect('seleccion')

    order_id = order_data.get('order_id', 'N/A')
    
    encoded_qrs_with_data = []
    
    try:
        # Intenta abrir el logo una sola vez
        logo = Image.open(LOGO_PATH)
    except FileNotFoundError:
       
        logo = None
        print(f"Advertencia: No se encontró el archivo del logo en la ruta: {LOGO_PATH}")
        
    #PASO CLAVE 2: Iterar sobre los datos de los empleados de la sesión
    for empleado in resumen_empleados:
        try:
            # Prepara la información para el QR (incluye el ID de la orden si es relevante)
            info = (
                f"Orden ID: {order_id}\n" # Incluimos la referencia a la orden recién creada
                f"Empleado: {empleado.get('employees', 'N/A')}\n"
                f"Cédula: {empleado.get('cedula', 'N/A')}\n"
                f"Almuerzo: {empleado.get('lunch', 'No')}\n"
                f"Para Llevar: {empleado.get('to_go', 'No')}\n"
                f"Cubiertos: {empleado.get('covered', 'No')}"
            )
            
            # --- Generación del QR (Tu código actual) ---
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
            qr.add_data(info)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
            
            if logo:
                qr_width, qr_height = qr_img.size
                logo_size = int(qr_width * 0.40)
                logo_resized = logo.copy()
                logo_resized.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
                logo_pos = ((qr_width - logo_resized.width) // 2, (qr_height - logo_resized.height) // 2)
                # Usamos el logo_resized como máscara
                qr_img.paste(logo_resized, logo_pos, logo_resized)
            
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            encoded_img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Almacenamos el nombre y el QR codificado
            encoded_qrs_with_data.append({
                'employee_name': empleado.get('employees', 'Empleado'),
                'qr_code': encoded_img_data,
                'cedula': empleado.get('cedula', 'N/A')
            })
            
        except Exception as e:
            print(f"Error generando QR para empleado: {e}")
            continue

    #PASO CLAVE 3: Limpiar los datos de la sesión después de usarlos
    if 'resumen_empleados' in request.session:
        del request.session['resumen_empleados']
    if 'order_data_for_ticket' in request.session:
        del request.session['order_data_for_ticket']

    # PASO CLAVE 4: Renderizar la plantilla FINAL de los tiques
    contexto = {
        'tickets': encoded_qrs_with_data,
        'order_id': order_id,
        'current_page': 'ticket' 
    }
        
    return render(request, 'paginas/ticket.html', contexto)
    
def empleados(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 

    
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    processed_employees = []
    try:
        response = requests.get(f"{api_url}/empleados", headers=headers, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        
        data_principal = json_data.get('employees', [])
        
        for names_lasname in data_principal:
                full_first_name = names_lasname.get("first_name")
                full_last_name = names_lasname.get("last_name")
                
                # Safely split and concatenate the names
                first_name = full_first_name.split()[0] if full_first_name else ""
                first_last_name = full_last_name.split()[0] if full_last_name else ""
                
                # Combine into a full name
                full_name = f"{first_name} {first_last_name}".strip()
                
                # Add the full name to the current employee's dictionary
                names_lasname['full_name'] = full_name
                print(names_lasname)
                # Append the processed employee data to the new list
                processed_employees.append(names_lasname)
       
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error inesperado: {req_err}")

    return render(request, 'paginas/empleados.html' , {'data_principal': processed_employees ,'current_page' : 'empleados'} )

def pedidos(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 

    
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    pedidos = []
    try:
        response = requests.get(f"{api_url}/pedidos", headers=headers, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        
        pedidos = json_data.get('orders', [])
          
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"error inesperado no se encontraron registros" )
    return render(request, "paginas/pedidos.html" ,{'current_page' : 'pedidos', 'pedidos':pedidos})

def extras(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 
       
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    if request.method == 'POST': 
       
        numberOrdersDay = request.POST.get ('numberOrdersDay')

       
        if not all([numberOrdersDay]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('usu') 

        data = {
            'numberOrdersDay': numberOrdersDay
        }

        try:
            
            response = requests.post(f"{api_url}/ordersDay", json=data, headers=headers, timeout=10)
            response.raise_for_status() 
            show_limit = response.json()
            print(show_limit)
            messages.success(request, 'cantidad de pedidos registrado.')
            return redirect('extras')
        except Exception as e:
            messages.error(request, 'Limite de registro al dia es uno')
            return redirect('extras')
        
        
        
    return render(request, "paginas/extras.html",{'current_page' : 'extras'}) 

def view_extras(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 
       
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(f"{api_url}/ordersDay", headers=headers, timeout=10)
        print(response)
        response.raise_for_status() 
        show_limit = response.json()
        
        limites = show_limit.get('cantidadOrdenes', [])
        print(limites)
        contexto = {
            'current_page': 'extras',
            'limites': limites
        }
       
        return render(request, "paginas/extras.html", contexto) 
    except Exception as e:
        messages.error(request, 'Error al traer la información.')
        return redirect('extras')

def ver_extras(request):
    
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 
       
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }    
        
    extras_list = []

    try:
        response = requests.get(f"{api_url}/extras", headers=headers, timeout=10)
        response.raise_for_status()         
        extras_list = response.json() 
        
        print(extras_list) 
        
    except requests.exceptions.RequestException as e:
       
        messages.error(request, f"Error al consultar los extras: {e}") 
        
    context = {
       
        'extras': extras_list 
    }
    
    return render(request, "paginas/extras.html", context)
                 
def regis_extras(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 
       
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    if request.method == 'POST': 
       
        precio = request.POST.get('precio')
        print(precio)
        extras = request.POST.get('extras')
        print(extras)
       
        if not all([precio,extras]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('extras') 

        data = {
            'nameExtra': extras,
            'price':precio
        }

        try:
            
            response = requests.post(f"{api_url}/extras", json=data, headers=headers, timeout=10)
            response.raise_for_status() 
                   
            messages.success(request, 'cantidad de pedidos registrado.')
            return redirect('extras')
        except Exception as e:
            messages.error(request, 'Limite de registro al dia es uno')
            return redirect('extras')
            
def escaner(request):
    return render(request,"paginas/scan.html",{'current_page' : 'escaner'})

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('inicio')



