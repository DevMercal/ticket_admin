
Este proyecto es una aplicación web construida con Django que sirve como un sistema de gestión de pedidos y tickets de comida, con un enfoque en el consumo de empleados. La aplicación se integra con una API externa (cuyo endpoint se define en settings.API) para manejar la autenticación, la gestión de usuarios, empleados, menús, pedidos y extras.

*Características Principales*

Autenticación de Usuarios: Permite el inicio de sesión (login) y la gestión de la sesión mediante un token de API.

Gestión de Usuarios y Empleados: Vistas para listar, registrar, y eliminar usuarios (administradores) y listar empleados.

Gestión de Menús: Permite el registro masivo (bluk) y la actualización de los ingredientes del menú diario.

Sistema de Pedidos:

Selección de empleados por gerencia.

Resumen del pedido con opciones de consumo (lunch, to_go, covered).

Registro de órdenes en bloque (bluk) a la API.

Generación de Tickets con QR: Genera un ticket único con un código QR (utilizando qrcode y PIL) para cada orden registrada, asociando el número de orden. * Reporte de Progreso: Muestra un gráfico de tarta (donut) para el progreso mensual (ejemplo estático en la vista progreso_mensual_view). * Gestión de Extras: Permite registrar extras y precios, así como establecer el límite de pedidos diarios.

🛠️ Tecnologías Utilizadas
Backend: Python, Django ,js

Peticiones HTTPS: requests

Gráficos: matplotlib

Generación de QR: qrcode, Pillow (PIL)

Serialización de Datos: json, base64

⚙️ Configuración e Instalación
Requisitos Previos
asgiref==3.9.2
Django==5.2.7
dotenv==0.9.9
mysqlclient==2.2.7
python-dotenv==1.1.1
sqlparse==0.5.3
Pillow==11.3.0
requests==2.32.5
qrcode==8.2
matplotlib

Una API externa funcionando en la dirección configurada en settings.API.

1. Clonar el Repositorio
Bash

git clone = http://10.22.8.58/developers/ticket_admin.git
cd ticket
2. Crear y Activar Entorno Virtual (Recomendado)
Bash

python -m venv venv
# En Linux/macOS
source venv/bin/activate
# En Windows
venv\Scripts\activate
3. Instalar Dependencias
Se asume que las dependencias están listadas en un archivo requirements.txt. Si no existe, las dependencias principales son:

asgiref==3.9.2
Django==5.2.7
dotenv==0.9.9
mysqlclient==2.2.7
python-dotenv==1.1.1
sqlparse==0.5.3
Pillow==11.3.0
requests==2.32.5
qrcode==8.2
matplotlib
django-sslserver

4. Configuración de Django
Settings: Asegúrate de configurar la URL de tu API en settings.py:

Python

# settings.py
API="https://comedor.mercal.gob.ve/api/p1"
# ...
# Asegúrate de que STATIC_ROOT y STATIC_URL estén configurados, 
# especialmente para cargar el logo.png.
Archivos Estáticos: Asegúrate de tener una imagen de logo, por ejemplo, static/img/logo.png, ya que la vista ticket intenta cargarla desde settings.STATIC_ROOT.


5. Ejecutar el Servidor de Desarrollo

local:
python manage.py runserver
La aplicación estará disponible en http://127.0.0.1:8000/.

local por ip
python manage.py runserver xxx.x.x.x:8000

local por ssl:
python manage.py runsslserver xxx.x.x.x:8000

