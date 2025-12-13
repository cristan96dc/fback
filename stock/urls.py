# En stock/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('list', views.lista_productos, name='lista_productos'),

    path('tipo/crear/', views.crear_tipo, name='crear_tipo'),
    path('producto/crear/', views.crear_producto, name='crear_producto'),

    path('producto/<int:producto_id>/stock/', views.actualizar_stock, name='actualizar_stock'),

    path('crear_venta', views.crear_venta, name='venta'),
    path('ventas/historico/', views.consultar_ventas, name='consultar_ventas'),
# 🚨 NUEVA URL PARA EXPORTAR CSV/XLSX 🚨
    path('alertas/stock/', views.panel_alertas, name='panel_alertas'), # 👈 PANEL DE AVISOS

    path('producto/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),

    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/crear/', views.crear_cliente, name='crear_cliente'),
    path('clientes/editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    
    # 🚨 AÑADIR ESTA LÍNEA PARA PDF 🚨

    path('subir-imagen/', views.subir_imagen, name='subir_imagen'),


    path('api/productos/', views.api_productos),
]