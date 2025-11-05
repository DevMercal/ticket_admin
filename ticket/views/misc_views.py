from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
from django.conf import settings
from requests.exceptions import ConnectionError, HTTPError, Timeout
from datetime import date
api_url = settings.API

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
    
    
    hoy = date.today().isoformat()
    total_sales = 0.0 
    
    try:
        
        endpoint = f"{api_url}/pedidos"
        params = {'fecha': hoy} 
        print(params)
        response = requests.get(
            endpoint, 
            headers=headers, 
            params=params,
            timeout=10
        )
        
        response.raise_for_status() 
        
        json_data = response.json()
        
        orders = json_data.get('orders', []) 
        if orders:
            first_order = orders[0] 
            date_order = first_order.get('date_order')
            print(date_order)
            
                
        for order in orders:
           
            try:
                
                amount = float(order.get('total_amount', 0.0)) 
                total_sales += int(amount)
                
            except (ValueError, TypeError):
                
                print(f"Advertencia: Pedido con monto inválido: {order}") 
                continue
        
        if date_order == params:
                total_sales
        else: 
            print("error ho noy pedidos")        
    except requests.exceptions.HTTPError as http_err:
       
        error_msg = f"Error de la API al obtener pedidos "
        
    contexto = {
        'number': number,
        'datos_usuarios': json_data,  
        'total_sales':total_sales,
        'current_page': 'dashboard'
    }
    print(total_sales)
    return render(request, 'paginas/index.html', contexto)

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
        print(result)
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