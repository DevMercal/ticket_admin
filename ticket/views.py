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
            print(menu)
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
            for employee_data in employees:
                full_first_name = employee_data.get("first_name")
                full_last_name = employee_data.get("last_name")
                
                # Safely split and concatenate the names
                first_name = full_first_name.split()[0] if full_first_name else ""
                first_last_name = full_last_name.split()[0] if full_last_name else ""
                
                # Combine into a full name
                full_name = f"{first_name} {first_last_name}".strip()
                
                # Add the full name to the current employee's dictionary
                employee_data['full_name'] = full_name
                
                # Append the processed employee data to the new list
                processed_employees.append(employee_data)
       
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
    
        if total > 0:
            resumen_empleados = []
            
            for i in range(total): 
                employees_id = request.POST.get(f'employees_{i}')
               
                
                if not employees_id:
                    continue 
                
                lunch = request.POST.get(f'lunch_{i}', 'No')
                to_go = request.POST.get(f'to_go_{i}', 'No')
                covered = request.POST.get(f'covered_{i}', 'No')
                
                
                if lunch == 'No' and to_go == 'No' and covered == 'No':
                    continue

                resumen_empleados.append({
                    'employees': employees_id,
                    'lunch': lunch,
                    'to_go': to_go,
                    'covered': covered,
                })
            
            # Guardar el resumen en la sesión solo si hay empleados válidos
            if resumen_empleados:
                request.session['resumen_empleados'] = resumen_empleados
                contexto = {
                    'contexto': resumen_empleados,
                    'current_page': 'resumen'
                }
               
                    
                return render(request, 'paginas/resumen.html', contexto)
        
        # Redirigir si 'total_employees' es 0 o si no se seleccionaron opciones
        messages.warning(request, "No se seleccionó ninguna opción. Por favor, seleccione un empleado para continuar.")
        return redirect('seleccion')
        
    # Redirigir si el método no es POST
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
            return redirect('ticket')
            
        try:
            # cedula: 'required|numeric'
            cedula = str(int(request.POST.get('cedula') or 0))
        except ValueError:
            messages.error(request, " Error: El campo 'Cédula de la Orden' debe ser un número entero.")
            return redirect('ticket')

        try:
            # IDs: Convertidos a STRING
            id_payment_method = str(int(request.POST.get('id_payment_method') or 0))
            id_order_status = str(int(request.POST.get('id_order_status', '1')))
            id_orders_consumption = str(int(request.POST.get('id_orders_consumption', '1')))
        except ValueError:
            messages.error(request, " Error: Los IDs de pago o estado deben ser números enteros.")
            return redirect('ticket')
            
        # --- Campos de EmployeePayment (STRING) ---
        cedula_employee = request.POST.get('cedula_employee')
        name_employee = request.POST.get('name_employee')
        phone_employee = request.POST.get('phone_employee', '')
        management = request.POST.get('management') 
        extras = request.POST.get('extras', '1') # Lo incluimos aunque no esté en la validación
        
        payment_support = request.FILES.get('payment_support')
        
        
        # 2. CONSTRUIR el payload PLANO (Claves de Laravel)
        # ESTO REEMPLAZA a payload_data, json.dumps() y data_to_send anterior.
        data_to_send = {
           
            'order[special_event]': special_event,
            'order[authorized]': authorized,
            'order[authorized_person]': authorized_person,
            'order[id_payment_method]': str(id_payment_method), 
            'order[reference]': str(reference), 
            'order[total_amount]': total_amount, 
            'order[cedula]': str(cedula), 
            'order[id_order_status]': str(id_order_status), 
            'order[id_orders_consumption]': str(id_orders_consumption),
            
            # --- Claves de employeePayment con NOTACIÓN DE ARRAY ---
            'employeePayment[cedula_employee]': cedula_employee,
            'employeePayment[name_employee]': name_employee,
            'employeePayment[phone_employee]': phone_employee,
            'employeePayment[management]': management,
            
            # --- Extras ---
            'extras[]': extras, 
        }

        # 3. Preparar los archivos (Clave de Laravel para el archivo con notación de array)
        files_to_send = {}
        if payment_support:
            content_type = mimetypes.guess_type(payment_support.name)[0] or 'application/octet-stream'
            
            # ¡CLAVE! El archivo también debe usar la notación de array
            files_to_send = {
                'order[payment_support]': (payment_support.name, payment_support.file, content_type)
            }
        
       
        try:
            # Enviamos data (datos planos con claves de array) y files (archivo)
            response = requests.post(
                f"{api_url}/pedidos", 
                headers=headers, 
                data=data_to_send, 
                files=files_to_send, 
                timeout=10
            )
            response.raise_for_status()

            messages.success(request, "La orden se ha registrado correctamente. ")
            return redirect('ticket')

        except requests.exceptions.HTTPError as err:
            # La depuración es esencial
            print(f"Error {response.status_code} - Respuesta de la API: {response.text}") 
            
            error_msg = f"Error: {response.status_code}. Detalles no disponibles."
            try:
                error_data = response.json()
                # Mostrar el detalle del error de validación
                error_msg = error_data.get('message', error_msg)
                
                if 'errors' in error_data:
                    validation_errors = [f"{k}: {', '.join(v)}" for k, v in error_data['errors'].items()]
                    error_msg += " | Detalles: " + " | ".join(validation_errors)

            except:
                pass
            messages.error(request, f" Error al registrar: {error_msg}")

        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexión con la API de órdenes.")
            print(f"Error de conexión: {e}")

    return render(request, "paginas/ticket.html")


LOGO_PATH = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png')


def ticket(request):
    
    if request.method == 'POST':
        
        employee_names = request.POST.getlist('employees')
        lunch_options = request.POST.getlist('lunch')
        to_go_options = request.POST.getlist('to_go')
        covered_options = request.POST.getlist('covered')
        
        encoded_qrs = []
        
        
        try:
            logo = Image.open(LOGO_PATH)
        except FileNotFoundError:
           
            logo = None
            print(f"Advertencia: No se encontró el archivo del logo en la ruta: {LOGO_PATH}")
            
        for i in range(len(employee_names)):
            try:
                info = (
                    f"Empleado: {employee_names[i]}\n"
                    f"Almuerzo: {lunch_options[i]}\n"
                    f"Para Llevar: {to_go_options[i]}\n"
                    f"Cubiertos: {covered_options[i]}"
                )
                
               
                qr = qrcode.QRCode(
                    error_correction=qrcode.constants.ERROR_CORRECT_H
                )
                qr.add_data(info)
                qr.make(fit=True)
                
                
                qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
                
               
                if logo:
                    qr_width, qr_height = qr_img.size
                    
                    
                    logo_size = int(qr_width * 0.40)
                    logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
                    
                    # Calcular la posición para centrar el logo
                    logo_pos = ((qr_width - logo.width) // 2, (qr_height - logo.height) // 2)
                    
                    # Pegar el logo sobre el QR, usando el propio logo como máscara
                    qr_img.paste(logo, logo_pos, logo)
                
                # Guardar la imagen combinada en un buffer de memoria
                buffer = BytesIO()
                qr_img.save(buffer, format='PNG')
                
                # Codificar la imagen y añadirla a la lista
                encoded_img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                encoded_qrs.append(encoded_img_data)
                zipped_data = zip(employee_names, encoded_qrs) 
                
            except IndexError:
                print(f"Skipping incomplete data for employee at index {i}")
                continue
        
        return render(request, 'paginas/ticket.html',{
                'zipped_data': zipped_data,
                'current_page': 'ticket' , 
                
                } )
    
    messages.warning(request, "Advertencia: Para crear un ticket, primero debe seleccionar un empleado")
    return redirect('seleccion')
    



def empleados(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 

    
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f"{api_url}/empleados", headers=headers, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        # 1. Acceder al primer 'data' y luego al segundo 'data'
        data_principal = json_data.get('employees', [])
       
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error inesperado: {req_err}")

    return render(request, 'paginas/empleados.html' , {'data_principal': data_principal ,'current_page' : 'empleados'} )


def pedidos(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 

    
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f"{api_url}/pedidos", headers=headers, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        
        pedidos = json_data.get('orders', [])
          
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error inesperado: {req_err}" )
    return render(request, "paginas/pedidos.html" ,{'current_page' : 'pedidos', 'pedidos':pedidos})


def extras(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 
    
    if request.method == 'POST':
        coverd = request.POST.get ('cubiertos')
        to_go = request.POST.get ('para_llevar')
        
        print(coverd)
        print(to_go)
    
    return render(request, "paginas/pedidos.html") 

def escaner(request):
    return render(request,"paginas/scan.html",{'current_page' : 'escaner'})


#logout de la aplicacion
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('inicio')