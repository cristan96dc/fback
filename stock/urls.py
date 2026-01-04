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
    

 

    
    # CHOFERES
    path('choferes/', views.lista_choferes, name='lista_choferes'),
    path('choferes/crear/', views.crear_chofer, name='crear_chofer'),
    path('choferes/editar/<int:chofer_id>/', views.editar_chofer, name='editar_chofer'),
    
    # ENVÍOS
    path('envios/', views.lista_envios, name='lista_envios'),
    path('envios/crear/', views.crear_envio, name='crear_envio'),
    path('envios/<int:envio_id>/', views.detalle_envio, name='detalle_envio'),
    path('envios/<int:envio_id>/estado/', views.actualizar_estado_envio, name='actualizar_estado_envio'),
    path('envios/programa/', views.programa_dia, name='programa_dia'),

    # 🚨 AÑADIR ESTA LÍNEA PARA PDF 🚨

    path('subir-imagen/', views.subir_imagen, name='subir_imagen'),


    path('api/productos/', views.api_productos),



]