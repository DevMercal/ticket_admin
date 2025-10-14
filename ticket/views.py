from datetime import date
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
                name = empleados.get('first_name')
                
                email = empleados.get('email')
                
                if token:
                    
                    request.session['api_token'] = token
                    request.session['first_name'] = name
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
    ax.text(0, 0, f'{completado}%', ha='center', va='center', fontsize=40, color='green', weight='bold')
    ax.text(0, -0.2, 'Objetivo', ha='center', va='center', fontsize=20, color='gray')

    # Crear la leyenda
    legend_elements = [
        mpatches.Patch(facecolor=colores[0], label=f'{etiquetas[0]}   {completado}%'),
        mpatches.Patch(facecolor=colores[1], label=f'{etiquetas[1]}   {restante}%')
    ]
    ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.1),
              ncol=1, frameon=False, fontsize=12, labelcolor='gray')

    # Configurar el fondo y el título
    fig.patch.set_facecolor('#282c34')
    ax.set_facecolor('#282c34')
    ax.set_title('Progreso Mensual', fontsize=20, color='gray', weight='bold')
    ax.axis('equal')

    # Guardar el gráfico en un buffer en memoria en lugar de un archivo
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', transparent=True)
    buffer.seek(0)
    plt.close(fig) 

    
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
    
    # Obtener la fecha de hoy en formato AAAA-MM-DD para enviarla a la API
    hoy = date.today().isoformat()
    total_sales = 0.0 # Se inicializa a float para consistencia
    
    try:
        # 2. Llamada a la API con Filtrado (asumiendo que la API lo soporta)
        # La URL debería incluir un parámetro para filtrar por la fecha de hoy.
        # Ejemplo: /pedidos?fecha=2025-10-14
        endpoint = f"{api_url}/pedidos"
        params = {'fecha': hoy} # Parámetro de filtrado
        
        response = requests.get(
            endpoint, 
            headers=headers, 
            params=params, # Se envían los parámetros de filtrado
            timeout=10
        )
        
        # 3. Manejo de Errores HTTP
        response.raise_for_status() 
        
        # 4. Procesamiento de Datos
        json_data = response.json()
        # Asumiendo que la API devuelve los pedidos filtrados en una clave 'orders'
        orders = json_data.get('orders', []) 
        
        for order in orders:
            # Es buena práctica validar que el campo exista y sea numérico
            try:
                # Asegura que el valor se convierte a float para la suma
                amount = float(order.get('total_amount', 0.0)) 
                total_sales += int(amount)
                
            except (ValueError, TypeError):
                 # Manejar el caso donde 'total_amount' no es un número válido
                print(f"Advertencia: Pedido con monto inválido: {order}") 
                continue # Pasa al siguiente pedido
        

    except requests.exceptions.HTTPError as http_err:
        # Errores 4xx o 5xx de la API
        error_msg = f"Error de la API al obtener pedidos ({response.status_code}): {http_err}"
        messages.error(request, error_msg)
        print(error_msg)
    
    
    
    contexto = {
        'number': number,
        'datos_usuarios': json_data,  
        'total_sales':total_sales,
        'current_page': 'dashboard'
    }
    print(total_sales)
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
        return redirect('inicio') 

    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    resumen_empleados = request.session.get('resumen_empleados', []) 
    
    if not resumen_empleados and request.method == 'POST':
        messages.error(request, "No hay empleados en el resumen para registrar la orden.")
        return redirect('pedidos') 
        
    if request.method == 'POST':
       
        special_event = request.POST.get('special_event', 'No')
        authorized = request.POST.get('authorized', 'No')      
        authorized_person = request.POST.get('authorized_person', '')
        total_amount = request.POST.get('total_amount', '0.0') 

        try:
        # Usamos int() para asegurar que la referencia base sea un entero sin .0
         reference_base = str(int(request.POST.get('reference') or 0)) 
        except ValueError:
            messages.error(request, " Error: El campo 'Referencia' debe ser un número entero.")
            return redirect('pedidos')
                
        
        
        try:
            id_payment_method = str(int(request.POST.get('id_payment_method') or 0))
            id_order_status = str(int(request.POST.get('id_order_status', '1')))
            id_orders_consumption = str(int(request.POST.get('id_orders_consumption', '1')))
        except ValueError:
            messages.error(request, " Error: Los IDs de pago o estado deben ser números enteros.")
            return redirect('pedidos')
            
       
        cedula_employee = request.POST.get('cedula_employee')
        name_employee = request.POST.get('name_employee')
        phone_employee = request.POST.get('phone_employee', '')
        management = request.POST.get('management') 
        extras = request.POST.get('extras', '1') 
        
        payment_support = request.FILES.get('payment_support')
        
        
        
        orders = []
        
      
        try:
            total_float = float(total_amount)
            monto_unitario = total_float / len(resumen_empleados) if resumen_empleados else 0.0
            total_amount_unitario_str = "{:.2f}".format(monto_unitario)
        except (ValueError, ZeroDivisionError):
            messages.error(request, "Error en el cálculo del monto total o lista de empleados vacía.")
            return redirect('pedidos')


        
        for empleado_consumo in resumen_empleados:
            
            
            cedula_orden = str(empleado_consumo['cedula']) 
            employee_cedula = cedula_orden + reference_base
            
            data_for_json = {
                "order": {
                    'special_event': special_event,
                    'authorized': authorized,
                    'id_payment_method': id_payment_method,
                    'id_order_status':id_order_status,
                    'authorized_person': authorized_person,
                    'reference':employee_cedula,
                    'cedula': cedula_orden, 
                    'total_amount': total_amount_unitario_str,
                    'id_orders_consumption': str(id_orders_consumption),
                },
                "employeePayment": {
                    'cedula_employee': cedula_employee,
                    'name_employee': name_employee,
                    'phone_employee':phone_employee,
                    'management': management,
                },
                
                "extras": [extras] 
            }
            orders.append(data_for_json) 

      
        orders_json_string = json.dumps(orders)

       
        payload_data = {
            'orders_json': orders_json_string
        }
        
        
        files_to_send = []

        if payment_support:
           
            payment_support.file.seek(0)
            file_content = payment_support.file.read() 
            
            
            num_orders = len(orders) 
            content_type = mimetypes.guess_type(payment_support.name)[0] or 'application/octet-stream'
            file_name = payment_support.name
            
           
            for i in range(num_orders):
                
                files_to_send.append(
                    ('payment_supports[]', (f"soporte_{i}_{file_name}", file_content, content_type))
                )
                

        
        try:
            response = requests.post(
                f"{api_url}/pedidos/bluk", 
                headers=headers, 
                data=payload_data,   
                files=files_to_send, 
                timeout=10
            )
            
    
            
            try:
                response_data = response.json() # Convierte el JSON a un diccionario de Python
                print(response_data)
            except requests.exceptions.JSONDecodeError:
               
                print(response.text)
                
            
            
            response.raise_for_status() 
            
            # Si la respuesta es JSON, ya la tienes en 'response_data'
            request.session['order_data_for_ticket'] = response_data
            messages.success(request, "La orden se ha registrado correctamente")
            return redirect('ticket')

        except requests.exceptions.HTTPError as err:
             
            error_msg = f"Error: {response.status_code}. Detalles no disponibles."
            try:
                error_data = response.json()
               
                error_msg = error_data.get('message', error_msg)
                
                if 'errors' in error_data:
                    validation_errors = [f"{k}: {', '.join(v)}" for k, v in error_data['errors'].items()]
                    error_msg += " | Detalles: " + " | ".join(validation_errors)

            except:
           
                pass 
            messages.error(request, f" Error al registrar: {error_msg}")

        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexión con la API de órdenes.")
            

    
    return render(request, "paginas/pedidos.html")

def ticket(request):
    
    if request.method != 'GET':
        messages.warning(request, "Acceso no válido.")
        return redirect('seleccion')
        
    
    resumen_empleados = request.session.get('resumen_empleados', [])
    order_data = request.session.get('order_data_for_ticket', {})
    
    
    order_ids = order_data.get('orders', []) 
    
    
    if not resumen_empleados:
        messages.warning(request, "No hay empleados registrados para generar ticket.")
        
        if 'order_data_for_ticket' in request.session:
             del request.session['order_data_for_ticket']
        return redirect('seleccion')

    # Validación de seguridad: Asegurar que el número de empleados coincida con el de órdenes.
    if len(resumen_empleados) != len(order_ids):
        # Manejo de error si la API no devolvió la cantidad esperada
        messages.error(request, f"Error: La API devolvió {len(order_ids)} IDs de orden, pero se registraron {len(resumen_empleados)} empleados. Se usarán IDs genéricos.")
        # Creamos una lista de None o 'N/A' para evitar errores de índice
        order_ids = [None] * len(resumen_empleados) 
        
    encoded_qrs_with_data = []
    
    try:
        logo = Image.open(LOGO_PATH)
    except FileNotFoundError:
        logo = None
        print(f"Advertencia: No se encontró el archivo del logo en la ruta: {LOGO_PATH}")
        
    # PASO CLAVE 2: Iterar sobre empleados y IDs de orden *simultáneamente*
    # zip() empareja (empleado[0], order_id[0]), (empleado[1], order_id[1]), etc.
    for empleado, order_id in zip(resumen_empleados, order_ids):
        try:
           
            current_order_id = str(order_id) if order_id is not None else 'N/A'
            
            
            info = (
                f"Orden ID: {current_order_id}\n" 
                f"Empleado: {empleado.get('employees', 'N/A')}\n"
                f"Cédula: {empleado.get('cedula', 'N/A')}\n"
                f"Almuerzo: {empleado.get('lunch', 'No')}\n"
                f"Para Llevar: {empleado.get('to_go', 'No')}\n"
                f"Cubiertos: {empleado.get('covered', 'No')}"
            )
            
            # --- Código de Generación de QR (sin cambios) ---
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
            
            # Almacenamos el nombre, el QR codificado y el ID de orden individual
            encoded_qrs_with_data.append({
                'employee_name': empleado.get('employees', 'Empleado'),
                'qr_code': encoded_img_data,
                'cedula': empleado.get('cedula', 'N/A'),
                'order_id': current_order_id  # ⬅️ Guardamos el ID individual para el template
            })
            
        except Exception as e:
            print(f"Error generando QR para empleado: {e}")
            continue

    
     # PASO 3: Limpiar los datos de la sesión
    if 'resumen_empleados' in request.session:
        del request.session['resumen_empleados']
    if 'order_data_for_ticket' in request.session:
        del request.session['order_data_for_ticket']

    # PASO 4: Renderizar la plantilla FINAL
    # NOTA: Ahora no se pasa un 'order_id' único, sino que cada ticket tiene su propio ID
    contexto = {
        'tickets': encoded_qrs_with_data,
        # Si quieres mostrar un rango (ej: "Órdenes 39 a 41"):
        'order_range': f"Órdenes {order_ids[0]} - {order_ids[-1]}" if order_ids else 'N/A',
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
                
                
                first_name = full_first_name.split()[0] if full_first_name else ""
                first_last_name = full_last_name.split()[0] if full_last_name else ""
                
                
                full_name = f"{first_name} {first_last_name}".strip()
                
                
                names_lasname['full_name'] = full_name
                
               
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

def extras_unified_view(request):
    # 1. Verificación de Autenticación y Encabezados Comunes
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio')
       
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Inicialización del Contexto
    contexto = {
        'current_page': 'extras',
        'limites': None,      # Para el límite de pedidos diarios
        'extras': []          # Para la lista de extras registrados
    }

    # 2. Manejo de la Solicitud POST (Registro de Datos)
    if request.method == 'POST': 
        # Identificar qué formulario se ha enviado
        # Usaremos la presencia de campos específicos para distinguir
        
        # --- Lógica de registro de Límite de Pedidos (de la función 'extras_management') ---
        if 'numberOrdersDay' in request.POST:
            numberOrdersDay = request.POST.get('numberOrdersDay')
           
            if not numberOrdersDay:
                messages.error(request, 'El campo de límite de pedidos es obligatorio.')
                return redirect('extras_unified_view') 

            data = {'numberOrdersDay': numberOrdersDay}

            try:
                response = requests.post(f"{api_url}/ordersDay", json=data, headers=headers, timeout=10)
                response.raise_for_status() 
                messages.success(request, 'Cantidad de pedidos registrada.')
                return redirect('extras_unified_view')
            except requests.exceptions.HTTPError as e:
                messages.error(request, f'Error al registrar el límite de pedidos: {e}')
                return redirect('extras_unified_view')
            except Exception as e:
                messages.error(request, 'Ocurrió un error inesperado al registrar el límite.')
                return redirect('extras_unified_view')

        # --- Lógica de registro de Extras Adicionales (de la función 'regis_extras') ---
        elif 'extras' in request.POST and 'precio' in request.POST:
            precio = request.POST.get('precio')
            extras_name = request.POST.get('extras')
           
            if not all([precio, extras_name]):
                messages.error(request, 'Los campos de extra y precio son obligatorios.')
                return redirect('extras_unified_view') 

            data = {
                'nameExtra': extras_name,
                'price': precio
            }

            try:
                response = requests.post(f"{api_url}/extras", json=data, headers=headers, timeout=10)
                response.raise_for_status() 
                messages.success(request, 'Extra registrado correctamente.')
                return redirect('extras_unified_view')
            except Exception as e:
                messages.error(request, f'Error al registrar el extra: {e}')
                return redirect('extras_unified_view')
        
        else:
            # POST sin campos reconocidos
            messages.error(request, 'Solicitud POST no válida.')
            return redirect('extras_unified_view')

    result = []
    try:
        response_limit = requests.get(f"{api_url}/ordersDay", headers=headers, timeout=10)
        response_limit.raise_for_status() 
        
        limite = response_limit.json() 
        resultado = limite.get('remainingTotal')
        
        total_all = limite.get('totalAllowed')
        date = limite.get('totalSold')
        
        result ={
            'resultado':resultado,
            'total_all':total_all,
            'date':date
        }
        
    except requests.exceptions.RequestException:
        messages.warning(request, 'No se pudo obtener la información del límite diario.')
        
    
    try:
        response_extras = requests.get(f"{api_url}/extras", headers=headers, timeout=10)
        response_extras.raise_for_status()         
        extras = response_extras.json() 
        resultados = extras.get('extras',[])
        contexto={
            'resultados': resultados
        }
        contexto.update(result)
    except requests.exceptions.RequestException:
        messages.warning(request, 'No se pudo obtener la lista de extras.')

    
    return render(request, "paginas/extras.html",contexto)

def escaner(request):
    return render(request,"paginas/scan.html",{'current_page' : 'escaner'})

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('inicio')


