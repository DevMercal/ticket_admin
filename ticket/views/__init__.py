# Importa todas las vistas para que puedan ser accedidas desde <app_name>.views
from .auth_views import inicio, logout_view
from .user_views import usu, user_registro, eliminar_user
from .menu_views import menu, registro_menu, actualizar_menu
from .order_views import registration_order, pedidos, resumen, ticket
from .employee_views import empleados, seleccion
from .misc_views import index, progreso_mensual_view, extras_unified_view, escaner