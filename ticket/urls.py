from django.urls import path
from .views import *
urlpatterns = [
    path('', inicio , name='inicio'),
    path('index', index , name='index'),
    path('progreso-grafico/', progreso_mensual_view, name='progreso-grafico'),
    path('usu', usu , name='usu'),
    path('registro_menu' , registro_menu , name='registro_menu' ),
    path('user_registro', user_registro , name='user_registro'),
    path('eliminar_user/<int:id>', eliminar_user , name='eliminar_user'),    
    path('menu', menu , name='menu'),
    path('eliminar_menu/<str:date_menu>', actulizar_menu , name="eliminar_menu"),
    path('seleccion', seleccion , name='seleccion'),
    path('resumen', resumen, name='resumen'),
    path('registration_order', registration_order , name="registration_order"),
    path('ticket', ticket , name='ticket'),
    path('empleados' , empleados , name= 'empleados'),
    path('pedidos', pedidos , name="pedidos"),
    path('escaner', escaner, name="escaner"),
    path('logout_view' , logout_view , name='logout_view' )
]