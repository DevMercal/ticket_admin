from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from django.conf import settings
api_url = settings.API

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

def registro_menu(request):
    if request.method == 'POST':
        
        sopas = request.POST.getlist('sopas')
        contornos = request.POST.getlist('contornos')
        proteinas = request.POST.getlist('proteinas')
        postres = request.POST.getlist('postres') 
        bebidas = request.POST.getlist('bebidas')
        ensaladas = request.POST.getlist('ensaladas')
        
       
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
        agregar_al_payload("Ensaladas", ensaladas)
        
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

def actualizar_menu(request, id_menu):
    if request.method == 'POST':
       
        
        first_ingredient = request.POST.get('first_ingredient')

        
        payload = {
            "ingredient": first_ingredient,
        }
        print(payload)
        try:
            token = request.session.get('api_token')
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.patch(
                f"{api_url}/menus/{id_menu}", 
                headers=headers, 
                json=payload,
                timeout=10
            )
            print(response)
            response.raise_for_status()

            messages.success(request, f'Menú  actualizado exitosamente.')
            return redirect('menu')

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error al actualizar el menú: {e}")
           
    return render(request, "paginas/menu.html")