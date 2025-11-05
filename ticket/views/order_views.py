from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json
import qrcode
import base64
from io import BytesIO
from PIL import Image
import mimetypes
import os
from django.conf import settings
LOGO_PATH = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png')

api_url = settings.API

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
        
        # payment_support = request.FILES.get('payment_support')
        
        
        
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
        
                
        payload_to_send = {
            'orders_json': orders_json_string
        }
        print(payload_to_send)
        
        # files_to_send = []

        # if payment_support:
           
        #     payment_support.file.seek(0)
        #     file_content = payment_support.file.read() 
            
            
        #     num_orders = len(orders) 
        #     content_type = mimetypes.guess_type(payment_support.name)[0] or 'application/octet-stream'
        #     file_name = payment_support.name
            
           
        #     for i in range(num_orders):
                
        #         files_to_send.append(
        #             ('payment_supports[]', (f"soporte_{i}_{file_name}", file_content, content_type))
        #         )
                
        # print(files_to_send)
        
        try:
            response = requests.post(
                f"{api_url}/pedidos/bluk", 
                headers=headers, 
                json=payload_to_send  ,
                # files=files_to_send, 
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
            return redirect('seleccion')
        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexión con la API de órdenes.")
            return redirect('seleccion')

    
    return render(request, "paginas/pedidos.html")

def pedidos(request):
    # 1. Verificación de sesión
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
        response.raise_for_status() # Lanza un error para códigos 4xx/5xx
        json_data = response.json()

        pedidos = json_data.get('orders', [])
        

    except requests.exceptions.RequestException as req_err:
        
        messages.error(request, f"Error al comunicarse con la API: {req_err}")
        
   
    return render(request, "paginas/pedidos.html" ,{
        'current_page' : 'pedidos', 
        'pedidos': pedidos 
    })
    
def resumen(request):
    if request.method == 'POST':
        total = int(request.POST.get('total_employees', 0))
        
        total_pago_general = request.POST.get('total_pago_general')
        print(total_pago_general)
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


def ticket(request):
    """
    Genera un ticket para cada empleado con un código QR asociado a su número de orden.
    """
    
    # ... (Validación del método y obtención de datos de la sesión, puntos 1 a 4) ...
    if request.method != 'GET':
        messages.warning(request, "Acceso no válido. Solo se permite GET.")
        return redirect('seleccion') 
        
    resumen_empleados = request.session.get('resumen_empleados', [])
    order_data = request.session.get('order_data_for_ticket', {})
    order_data_items = order_data.get('orders', [])
    
    if not resumen_empleados:
        messages.warning(request, "No hay empleados registrados para generar ticket.")
        if 'order_data_for_ticket' in request.session:
             del request.session['order_data_for_ticket']
        return redirect('seleccion')

    if len(resumen_empleados) != len(order_data_items):
        error_msg = f"Inconsistencia de datos: La API devolvió {len(order_data_items)} órdenes, pero hay {len(resumen_empleados)} empleados. Usando datos genéricos."
        messages.error(request, error_msg)
        print(f"ERROR: {error_msg}")
        order_items_to_use = [{'number_order': 'N/A'}] * len(resumen_empleados) 
    else:
        order_items_to_use = order_data_items
        
    encoded_qrs_with_data = []
    
    # 5. Carga del logo (mejorado el manejo de excepciones)
    logo = None
    try:
        # Nota: Asume que LOGO_PATH y Image están correctamente importados
        logo_original = Image.open(LOGO_PATH).convert("RGBA")
        # Recomendación: Redimensionar el logo a un tamaño pequeño para el QR (e.g., 60x60 píxeles)
        logo = logo_original.resize((60, 60)) 
    except Exception as e:
        print(f"Advertencia/Error al cargar o redimensionar el logo: {e}")
        
    # 6. Generación de QRs: Iterar sobre empleados y datos de orden *simultáneamente*
    for empleado, order_data_item in zip(resumen_empleados, order_items_to_use):
        try:
            current_order_number = str(order_data_item.get('number_order', 'N/A'))
            info = f"Orden: {current_order_number}"  
            print(f"Generando QR para empleado: {current_order_number}")
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                # *** OPTIMIZACIÓN: Reducimos el tamaño de la caja (box_size) ***
                box_size=10,  # Cambiado de 5 a 3
                border=4,
            )
            qr.add_data(info)
            qr.make(fit=True)
            
            # Crear la imagen del QR y opcionalmente centrar el logo
            qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
            
            if logo:
                # Calcular posición para centrar el logo
                pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
                # La máscara del logo (el propio objeto 'logo') maneja la transparencia
                qr_img.paste(logo, pos, logo) 
            
            # Codificación a Base64
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            encoded_img_data = base64.b64encode(buffer.getvalue()).decode()
            
            
            encoded_qrs_with_data.append({
                'employee_name': empleado.get('employees', 'Empleado Desconocido'), 
                'qr_code': encoded_img_data, 
                'cedula': empleado.get('cedula', 'N/A'),
                'order_id': current_order_number  
            })
            
        except Exception as e:
            print(f"Error crítico generando QR para empleado {empleado.get('employees', 'Desconocido')}: {e}")
            messages.error(request, f"Error generando ticket para empleado {empleado.get('employees', 'Desconocido')}. Detalle: {e}")
            continue

    
     # 7. Limpiar los datos de la sesión
    if 'resumen_empleados' in request.session:
        del request.session['resumen_empleados']
    if 'order_data_for_ticket' in request.session:
        del request.session['order_data_for_ticket']
    if 'id_orders_consumption' in request.session:
        del request.session['id_orders_consumption']

    
    contexto = {
        'tickets': encoded_qrs_with_data,
        'order_range': order_data_items, 
        'current_page': 'ticket' 
    }
    
    return render(request, 'paginas/ticket.html', contexto)