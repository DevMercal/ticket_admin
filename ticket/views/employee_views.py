from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from django.conf import settings
api_url = settings.API

def seleccion(request):
    if 'api_token' not in request.session:
        messages.warning(request, "Debe iniciar sesión para ver esta información.")
        return redirect('inicio')

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
        
    try:
        response_bcv = requests.get(f"{api_url}/dolar-bcv", headers=headers, timeout=10)
        response_bcv.raise_for_status()
        json_bcv = response_bcv.json()
        bcv_data = json_bcv.get('data', {})
        bcv_rate = bcv_data.get('rate', 'N/A')
        print(f"Tasa BCV obtenida: {bcv_rate}")
    except requests.exceptions.RequestException as req_err:
        bcv_rate = 'N/A'
        messages.warning(request, f"No se pudo obtener la tasa del BCV: {req_err}")
    return render(request, 'paginas/seleccion.html', {
        'bcv_rate': bcv_rate,
        'management': management,
        'selected_management': selected_management,
        'employees': processed_employees, 
        'current_page' : 'seleccion'})
   
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