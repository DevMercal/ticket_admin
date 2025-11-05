from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from django.conf import settings
api_url = settings.API

def usu(request: HttpRequest):
   
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio')  
    
    token = request.session.get('api_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
      
    usuarios =[] 
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
       
        cedula = request.POST.get('cedula', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password_confirmation = request.POST.get('password_confirmation', '')
        
       
        if not all([cedula, email, password, password_confirmation,]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('usu') 

        data = {
            'email': email,
            'password': password,
            'password_confirmation': password_confirmation,
            'cedula': cedula,
        }
        print(data)
        try:
            
            response = requests.post(f"{api_url}/users", json=data, headers=headers, timeout=10)
            print(response)
            response.raise_for_status()  # This will raise an HTTPError for 4xx/5xx status codes
            
            messages.success(request, 'Usuario registrado exitosamente.')
            return redirect('usu')

        except requests.exceptions.HTTPError as e:
            # Handle HTTP-specific errors (e.g., 400 Bad Request, 401 Unauthorized)
            try:
                json_data = response.json()
                error_message = json_data.get('message', 'Error al registrar el usuario.')
                messages.error(request, error_message)
                return redirect('usu')
            except requests.exceptions.JSONDecodeError:
                # Handle cases where the response isn't valid JSON
                messages.error(request, f'Error del servidor: {response.text}')
                return redirect('usu')
        except requests.exceptions.RequestException as e:
            # Catch all other request-related errors (e.g., connection, DNS)
            messages.error(request, f'Error de conexión con la API: {e}')
            return redirect('usu')
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