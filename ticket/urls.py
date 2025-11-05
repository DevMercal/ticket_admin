from django.urls import path
from .views import * # Esta línea sigue funcionando!

urlpatterns = [
    # Vistas de Autenticación
    path('', inicio , name='inicio'),
    path('logout_view' , logout_view , name='logout_view' ),
    
    # Vistas de Dashboard/Misceláneo
    path('index', index , name='index'),
    path('progreso-grafico/', progreso_mensual_view, name='progreso-grafico'),
    path('escaner', escaner, name="escaner"),
    path('extras_unified_view', extras_unified_view , name="extras_unified_view"),
    
    # Vistas de Usuarios (CRUD)
    path('usu', usu , name='usu'),
    path('user_registro', user_registro , name='user_registro'),
    path('eliminar_user/<int:id>', eliminar_user , name='eliminar_user'),    
    
    # Vistas de Menú
    path('menu', menu , name='menu'),
    path('registro_menu' , registro_menu , name='registro_menu' ),
    path('actulizar_menu/<int:id_menu>', actualizar_menu , name="actulizar_menu"),
    
    # Vistas de Empleados y Selección
    path('empleados' , empleados , name= 'empleados'),
    path('seleccion', seleccion , name='seleccion'),
    
    # Vistas de Pedidos/Órdenes
    path('resumen', resumen, name='resumen'),
    path('registration_order', registration_order , name="registration_order"),
    path('pedidos', pedidos , name="pedidos"),
    path('ticket', ticket , name='ticket'),
]