from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import  logout
from django.contrib import messages
import requests
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

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('inicio')