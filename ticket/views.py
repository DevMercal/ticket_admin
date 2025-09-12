from datetime import datetime
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import  logout
from django.contrib import messages
import requests
from django.core.paginator import Paginator
import qrcode
from io import BytesIO
import base64
from django.conf import settings

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
            
            response = requests.post(f"{api_url}/users/login", json=data, timeout=10)
            print(response)
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


  

def index(request):
    return render(request, 'paginas/index.html')


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
        print (json_data)
        usuarios = json_data.get('data', [])
        print(usuarios)
   
    except requests.exceptions.ConnectionError as conn_err:
        messages.error(request, f"Error de conexión: {conn_err} - No se pudo conectar con la API.")
            
    except requests.exceptions.Timeout as timeout_err:
        messages.error(request, f"Error de tiempo de espera: {timeout_err} - La solicitud tardó demasiado en responder.")
            
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error inesperado: {req_err}")

    # 5. Renderizamos la plantilla con los datos obtenidos (o una lista vacía en caso de error)
    return render(request, 'paginas/usuarios.html', {'usuarios': usuarios})




def user_registro(request: HttpRequest) -> HttpResponse:
 
    url = "http://comedor.mercal.gob.ve/api/p1/users"
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    if request.method == 'POST': 
        # Use .get() with a default value to prevent KeyError if a field is missing
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password_confirmation = request.POST.get('password_confirmation', '')
        id_management = request.POST.get('id_management', '')

        # Basic validation to ensure required fields aren't empty
        if not all([name, email, password, password_confirmation, id_management]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('usu') # Replace with your form view name

        data = {
            'name': name,
            'email': email,
            'password': password,
            'password_confirmation': password_confirmation,
            'id_management': id_management
        }

        try:
            # It's good practice to set a timeout for external requests
            response = requests.post(url, json=data, headers=headers, timeout=10)
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
        url = f"http://comedor.mercal.gob.ve/api/p1/users/{id}"
        token = request.session.get('api_token')
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.delete(url, headers=headers, timeout=10)
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
        
def registro(request):
    pass



def menu(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 

    url_api = "http://comedor.mercal.gob.ve/api/p1/menus"
    menus = []  
    token = request.session.get('api_token')
    
    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(url_api, headers=headers, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
       

        
        menus = json_data.get('menus', [])
       
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error inesperado: {req_err}")

    return render(request, 'paginas/menu.html', {'menus': menus})

    

def seleccion(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect(inicio)

    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    selected_management = request.GET.get('management', '')
    
    url_empleados = "http://comedor.mercal.gob.ve/api/p1/empleados"
    params = {'gerencias': selected_management} if selected_management else {}
    
    employees = []
    try:
        response = requests.get(url_empleados, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        json_data = response.json()
       
        employees = json_data.get('employees', [])
       
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error al obtener empleados: {req_err}")
    url_management = "http://comedor.mercal.gob.ve/api/p1/gerencias"
    management = []
    try:
        response_management = requests.get(url_management, headers=headers, timeout=10)
        response_management.raise_for_status()
        json_management = response_management.json()
        
        management = json_management.get('management', [])   
        
    except requests.exceptions.RequestException as req_err:
        messages.warning(request, f"No se pudo cargar la lista de gerencias: {req_err}")
    return render(request, 'paginas/seleccion.html', {
        'management': management,
        'selected_management': selected_management,
        'employees': employees    })


    
def resumen(request):
    if request.method == 'POST':
        # Esta línea lee el 'total_employees' que el JavaScript añadió
        total = int(request.POST.get('total_employees', 0))
       
        resumen_empleados = []
        
        
        for i in range(total): 
            employees = request.POST.get(f'employees_{i}')
            if not employees:
                continue 
            
            lunch = request.POST.get(f'lunch_{i}', 'No')
            to_go = request.POST.get(f'to_go_{i}', 'No')
            covered = request.POST.get(f'covered_{i}', 'No')

            resumen_empleados.append({
                'employees': employees,
                'lunch': lunch,
                'to_go': to_go,
                'covered': covered,
            })
            
            request.session['resumen_empleados'] = resumen_empleados

        contexto = {
            'contexto': resumen_empleados
        }

        return render(request, 'paginas/resumen.html', contexto)
    return redirect('seleccion')


def registration_order():
    pass



def ticket(request):
    
    if request.method == 'POST':
        
        employee_names = request.POST.getlist('employees')
        lunch_options = request.POST.getlist('lunch')
        to_go_options = request.POST.getlist('to_go')
        covered_options = request.POST.getlist('covered')
        
        encoded_qrs = []

      
        for i in range(len(employee_names)):
            try:
                
                info = (
                    f"Empleado: {employee_names[i]}\n"
                    f"Almuerzo: {lunch_options[i]}\n"
                    f"Para Llevar: {to_go_options[i]}\n"
                    f"Cubiertos: {covered_options[i]}"
                )
                
               
                qr_img = qrcode.make(info)
                buffer = BytesIO()
                qr_img.save(buffer, format='PNG')
                
               
                encoded_img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                encoded_qrs.append(encoded_img_data)

            except IndexError:
                
                print(f"Skipping incomplete data for employee at index {i}")
                continue
                
        
        return render(request, 'paginas/ticket.html', {'encoded_qrs': encoded_qrs})
    
   
    return render(request, 'paginas/error.html', {'message': 'Invalid request method.'})



def empleados(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio') 

    url_api = "http://comedor.mercal.gob.ve/api/p1/empleados"
    empleados = []
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(url_api, headers=headers, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        # 1. Acceder al primer 'data' y luego al segundo 'data'
        data_principal = json_data.get('employees', [])
        
        print(data_principal)
        
        
    except requests.exceptions.RequestException as req_err:
        messages.error(request, f"Ocurrió un error inesperado: {req_err}")

    return render(request, 'paginas/empleados.html' , {'data_principal': data_principal} )


#logout de la aplicacion
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('inicio')