from django.shortcuts import render
from django.db.models import F, Sum
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, TipoProducto,Cliente
from django.utils import timezone

def home(request):
    # 1. Traer la cantidad de productos que están en alerta
    #    (cantidad es menor que el umbral_alerta)
    productos_bajo_stock = Producto.objects.filter(
        cantidad__lt=F('umbral_alerta')
    ).count()
    
    # 2. Crear un booleano para el condicional en el HTML
    con_alerta = productos_bajo_stock > 0
    
    contexto = {
        'productos_bajo_stock': productos_bajo_stock,
        'con_alerta': con_alerta
    }
    
    return render(request, 'home.html', contexto)
# ----------------------------------
# LISTAR PRODUCTOS
# ----------------------------------
def lista_productos(request):
    # 1. Obtener todos los Tipos para el selector (select)
    tipos = TipoProducto.objects.all()
    
    # 2. Capturar los parámetros de búsqueda
    query_nombre = request.GET.get('nombre')
    query_tipo = request.GET.get('tipo')

    # 3. Iniciar la consulta
    productos = Producto.objects.select_related('tipo').all()

    # 4. Aplicar los filtros
    if query_nombre:
        # Busca productos cuyo nombre contenga la cadena (case-insensitive)
        productos = productos.filter(nombre__icontains=query_nombre)

    if query_tipo:
        # Filtra por el ID del tipo
        productos = productos.filter(tipo_id=query_tipo) 
        # Nota: La variable en el contexto la llamaremos 'query_tipo' para que coincida con el campo 'name="tipo"' del HTML

    return render(request, 'lista_productos.html', {
        'productos': productos,
        'tipos': tipos, # ✅ Pasar la lista de tipos para llenar el selector
        'query_nombre': query_nombre, # ✅ Pasar el nombre buscado para mantener el valor en el input
        'query_tipo': query_tipo,     # ✅ Pasar el ID del tipo seleccionado para marcar la opción
    })


# ----------------------------------
# CREAR TIPO DE PRODUCTO
# ----------------------------------
def crear_tipo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')

        if nombre:
            TipoProducto.objects.create(nombre=nombre)
            return redirect('lista_productos')

    return render(request, 'crear_tipo.html')


# ----------------------------------
# CREAR PRODUCTO
# ----------------------------------
def crear_producto(request):
    tipos = TipoProducto.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo_id = request.POST.get('tipo')
        cantidad = request.POST.get('cantidad')
        valor = request.POST.get('valor')
        
        # 🚨 NUEVO CAMPO: Capturar el umbral de alerta 🚨
        umbral_alerta = request.POST.get('umbral_alerta', 5) # Usamos 5 como default si el campo no viene
        
        # Aseguramos que umbral_alerta sea un entero, si no, usa el valor por defecto del modelo (5)
        try:
            umbral_alerta = int(umbral_alerta)
        except (ValueError, TypeError):
            umbral_alerta = 5 # Usa el valor seguro si la conversión falla

        if nombre and tipo_id:
            tipo = TipoProducto.objects.get(id=tipo_id)
            Producto.objects.create(
                nombre=nombre,
                tipo=tipo,
                cantidad=cantidad,
                valor=valor,
                # 🚨 PASAR EL NUEVO CAMPO AL CREADOR DEL OBJETO 🚨
                umbral_alerta=umbral_alerta
            )
            return redirect('lista_productos')

    return render(request, 'crear_producto.html', {'tipos': tipos})


# ----------------------------------
# ACTUALIZAR STOCK (SUMAR O RESTAR)
# ----------------------------------
def actualizar_stock(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad'))
        accion = request.POST.get('accion')  # sumar o restar

        if accion == 'sumar':
            producto.cantidad += cantidad
        elif accion == 'restar':
            producto.cantidad -= cantidad
            if producto.cantidad < 0:
                producto.cantidad = 0

        producto.fecha_modificacion = timezone.now()
        producto.save()
        return redirect('lista_productos')

    return render(request, 'actualizar_stock.html', {'producto': producto})

from .models import Producto, TipoProducto, Ventas
from django.contrib import messages

from django.shortcuts import render, redirect
from .models import Producto, TipoProducto, Ventas
from django.contrib import messages

# ----------------------------------
# CREAR VENTA
# ----------------------------------
 
# ... (otras importaciones)
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Producto, Cliente, Ventas # Asegúrate de que todas están importadas

# ----------------------------------
# CREAR VENTA
# ----------------------------------
def crear_venta(request):
    productos = Producto.objects.all().order_by('nombre')
    clientes = Cliente.objects.all().order_by('nombre_completo')

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cliente_id = request.POST.get('cliente')  
        
        try:
            cantidad = int(request.POST.get('cantidad'))
            producto = Producto.objects.get(id=producto_id)
        except (ValueError, Producto.DoesNotExist):
            messages.error(request, 'Error en los datos del producto o cantidad.')
            return redirect('venta') # 🚨 MODIFICADO: Usar el nombre de URL correcto
            
        # 1. Manejo del Cliente (Opcional)
        cliente = None
        if cliente_id:
            try:
                # El cliente_id viene del campo oculto 'cliente_id' que almacena el ID del cliente
                cliente = Cliente.objects.get(id=cliente_id) 
            except Cliente.DoesNotExist:
                messages.warning(request, 'Cliente no encontrado. Venta registrada sin cliente asignado.')
                pass 

        # 2. Validar Stock (la validación JS en el template ayuda, pero se valida en backend)
        if cantidad <= 0 or cantidad > producto.cantidad:
            messages.error(f'Stock insuficiente o cantidad no válida. Solo hay {producto.cantidad} disponibles.')
            return redirect('venta') # 🚨 MODIFICADO: Usar el nombre de URL correcto

        # 3. Calcular Total y Crear la Venta
        total = producto.valor * cantidad

        # Importante: Aquí 'cliente' debe ser el objeto Cliente (si se encontró) o None
        Ventas.objects.create(
            producto=producto,
            cliente=cliente, 
            cantidad=cantidad,
            valor_total=total
        )

        # 4. Restar Stock
        producto.cantidad -= cantidad
        producto.save()

        # 5. Mensaje de Éxito
        messages.success(request, f'Venta de {producto.nombre} por ${total:.2f} registrada correctamente.')
        
        # 🚨 MODIFICADO: Usar el nombre de URL correcto
        return redirect('venta') 

    # Si es método GET o después de POST exitoso/fallido
    return render(request, 'crear_venta.html', {
        'productos': productos,
        'clientes': clientes
    })

from django.db.models import Sum
from django.utils.dateparse import parse_datetime

import csv
from django.http import HttpResponse

# ... (otras funciones)
from django.db.models import Sum
# from django.utils.dateparse import parse_datetime # Esto no es necesario si solo usas request.GET
from .models import Ventas, Producto, Cliente # Asegúrate de importar Cliente
import csv
from django.http import HttpResponse

# --- Función Principal (consultar_ventas) ---
from django.db.models import Sum
# from django.utils.dateparse import parse_datetime # Esto no es necesario si solo usas request.GET
from .models import Ventas, Producto, Cliente # Asegúrate de importar Cliente
import csv
from django.http import HttpResponse

# --- Función Principal (consultar_ventas) ---
import csv
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows # Si usas pandas
import io # Para manejar la memoria del archivo Excel
from .models import Ventas, Producto, Cliente 

# ... (otras funciones)

# --- Función de Exportación principal (CSV/EXCEL) ---
from django.shortcuts import render
from django.db.models import Sum
from .models import Ventas, Producto, Cliente # Asumo que Ventas, Producto, Cliente están aquí

import csv
from django.http import HttpResponse
from openpyxl import Workbook
# from openpyxl.utils.dataframe import dataframe_to_rows # Solo si usas pandas, sino comenta o borra
# import io # Si usas io.BytesIO para manejar el archivo Excel en memoria

# ... Otras funciones (crear_venta, etc.) ...

# 🚨 FUNCIÓN FALTANTE QUE CAUSA EL ATTRIBUTEERROR 🚨
def consultar_ventas(request):
    productos = Producto.objects.all()
    clientes = Cliente.objects.all().order_by('nombre_completo')
    
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    cliente_id = request.GET.get('cliente')
    producto_id = request.GET.get('producto')

    # Lógica de Visibilidad: Solo se muestran si hay filtros o si se pulsó "Filtrar"
    if fecha_desde or fecha_hasta or cliente_id or producto_id or request.GET:
        
        ventas = Ventas.objects.all().order_by('-fecha')
        
        if fecha_desde:
            ventas = ventas.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            ventas = ventas.filter(fecha__date__lte=fecha_hasta)
        if cliente_id:
            ventas = ventas.filter(cliente_id=cliente_id) 
        if producto_id:
            ventas = ventas.filter(producto_id=producto_id)
            
        total_recaudado = ventas.aggregate(Sum('valor_total'))['valor_total__sum'] or 0

    else:
        ventas = Ventas.objects.none()
        total_recaudado = 0
        
    return render(request, 'consultar_ventas.html', {
        'ventas': ventas,
        'productos': productos,
        'clientes': clientes,
        'total_recaudado': total_recaudado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'cliente_id': cliente_id,
        'producto_id': producto_id,
    })


# ----------------------------------
# VISTA: PANEL DE AVISOS DE ALERTA (DEDICADO)
# ----------------------------------
def panel_alertas(request):
    # Trae los detalles completos de los productos que están bajo stock
    productos_con_alerta = Producto.objects.filter(
        cantidad__lt=F('umbral_alerta')
    ).select_related('tipo').order_by('nombre')
    
    contexto = {
        'productos_con_alerta': productos_con_alerta,
        'conteo_alertas': productos_con_alerta.count(),
    }
    
    return render(request, 'panel_alertas.html', contexto)


# ----------------------------------
# EDITAR PRODUCTO Y UMBRAL DE ALERTA (DEBE EXISTIR)
# ----------------------------------
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    tipos = TipoProducto.objects.all() 

    if request.method == 'POST':
        # ... (lógica de guardado)
        nombre = request.POST.get('nombre')
        tipo_id = request.POST.get('tipo')
        valor = request.POST.get('valor')
        umbral_alerta = request.POST.get('umbral_alerta') 
        
        producto.nombre = nombre
        producto.tipo_id = tipo_id 
        producto.valor = valor
        
        try:
            if umbral_alerta is not None:
                producto.umbral_alerta = int(umbral_alerta)
        except ValueError:
            messages.error(request, 'El umbral debe ser un número entero.')
            return redirect('editar_producto', producto_id=producto.id)
            
        producto.save()
        messages.success(request, f'Producto "{producto.nombre}" y umbral de alerta actualizados.')
        return redirect('lista_productos')

    return render(request, 'editar_producto.html', {
        'producto': producto,
        'tipos': tipos
    })

# ----------------------------------
# GESTIÓN DE CLIENTES
# ----------------------------------
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})


def crear_cliente(request):
    if request.method == 'POST':
        nombre_completo = request.POST.get('nombre_completo')
        nombre_local = request.POST.get('nombre_local')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        
        if nombre_completo:
            Cliente.objects.create(
                nombre_completo=nombre_completo,
                nombre_local=nombre_local if nombre_local else None,
                email=email if email else None,
                telefono=telefono if telefono else None,
                direccion=direccion if direccion else None
            )
            messages.success(request, 'Cliente creado correctamente')
            return redirect('lista_clientes')
    
    return render(request, 'crear_cliente.html')


def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        cliente.nombre = request.POST.get('nombre')
        cliente.apellido = request.POST.get('apellido')
        cliente.email = request.POST.get('email') or None
        cliente.telefono = request.POST.get('telefono') or None
        cliente.direccion = request.POST.get('direccion') or None
        cliente.save()
        
        messages.success(request, f'Cliente "{cliente.nombre_completo}" actualizado')
        return redirect('lista_clientes')
    
    return render(request, 'editar_cliente.html', {'cliente': cliente})

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Producto, ImagenProducto
import os
from django.conf import settings

import os
import uuid
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Producto, ImagenProducto

def subir_imagen(request):
    productos = Producto.objects.all()
    
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        imagen = request.FILES.get('imagen')
        
        if producto_id and imagen:
            try:
                producto = Producto.objects.get(id=producto_id)
                
                # Generar nombre único para evitar colisiones
                nombre_archivo = f"{uuid.uuid4()}{os.path.splitext(imagen.name)[1]}"
                ruta_relativa = f"productos/{nombre_archivo}"
                ruta_completa = os.path.join(settings.MEDIA_ROOT, ruta_relativa)
                
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
                
                # Guardar archivo
                with open(ruta_completa, 'wb+') as destino:
                    for chunk in imagen.chunks():
                        destino.write(chunk)
                
                # Eliminar imagen anterior si existe
                producto.imagenproducto_set.all().delete()
                
                # Guardar en BD
                ImagenProducto.objects.create(
                    producto=producto,
                    ruta=ruta_relativa  # Guardar solo la ruta relativa
                )
                
                messages.success(request, f'Imagen subida correctamente para {producto.nombre}')
            except Producto.DoesNotExist:
                messages.error(request, 'Producto no encontrado')
            except Exception as e:
                messages.error(request, f'Error al subir la imagen: {str(e)}')
        else:
            messages.error(request, 'Debe seleccionar un producto y una imagen')
        
        return redirect('subir_imagen')
    
    return render(request, 'imagenes/subir.html', {'productos': productos})


def api_productos(request):
    productos = Producto.objects.all()
    
    lista = []
    for p in productos:
        img = p.imagenproducto_set.first()
        
        imagen_url = None
        if img and img.ruta:
            # Construir URL completa usando MEDIA_URL
            imagen_url = request.build_absolute_uri(
                f'{settings.MEDIA_URL}{img.ruta}'
            )
        
        lista.append({
            'id': p.id,
            'nombre': p.nombre,
            'valor': float(p.valor),
            'imagen': imagen_url
        })
    
    return JsonResponse(lista, safe=False)




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Envio, DetalleEnvio, Chofer, Cliente, Producto
from django.utils import timezone
from datetime import date

# ----------------------------------
# CHOFERES
# ----------------------------------

def lista_choferes(request):
    """Lista todos los choferes"""
    choferes = Chofer.objects.all()
    return render(request, 'envios/lista_choferes.html', {'choferes': choferes})


def crear_chofer(request):
    """Crear un nuevo chofer"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo')
        telefono = request.POST.get('telefono')
        vehiculo = request.POST.get('vehiculo')
        notas = request.POST.get('notas')
        
        if nombre and telefono and vehiculo:
            Chofer.objects.create(
                nombre_completo=nombre,
                telefono=telefono,
                vehiculo=vehiculo,
                notas=notas
            )
            messages.success(request, 'Chofer creado correctamente')
            return redirect('lista_choferes')
        else:
            messages.error(request, 'Complete todos los campos obligatorios')
    
    return render(request, 'envios/crear_chofer.html')


def editar_chofer(request, chofer_id):
    """Editar un chofer existente"""
    chofer = get_object_or_404(Chofer, id=chofer_id)
    
    if request.method == 'POST':
        chofer.nombre_completo = request.POST.get('nombre_completo')
        chofer.telefono = request.POST.get('telefono')
        chofer.vehiculo = request.POST.get('vehiculo')
        chofer.notas = request.POST.get('notas')
        chofer.activo = request.POST.get('activo') == 'on'
        chofer.save()
        
        messages.success(request, f'Chofer "{chofer.nombre_completo}" actualizado')
        return redirect('lista_choferes')
    
    return render(request, 'envios/editar_chofer.html', {'chofer': chofer})


# ----------------------------------
# ENVÍOS
# ----------------------------------

def lista_envios(request):
    """Lista todos los envíos con filtros"""
    fecha = request.GET.get('fecha')
    chofer_id = request.GET.get('chofer')
    estado = request.GET.get('estado')
    
    envios = Envio.objects.select_related('cliente', 'chofer').all()
    
    # Aplicar filtros
    if fecha:
        envios = envios.filter(fecha_envio=fecha)
    else:
        # Por defecto mostrar envíos de hoy
        envios = envios.filter(fecha_envio=date.today())
    
    if chofer_id:
        envios = envios.filter(chofer_id=chofer_id)
    
    if estado:
        envios = envios.filter(estado=estado)
    
    # Para los selectores
    choferes = Chofer.objects.filter(activo=True)
    
    context = {
        'envios': envios,
        'choferes': choferes,
        'fecha': fecha or date.today(),
        'chofer_id': chofer_id,
        'estado': estado,
    }
    
    return render(request, 'envios/lista_envios.html', context)


def crear_envio(request):
    """Crear un nuevo envío"""
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        chofer_id = request.POST.get('chofer')
        fecha_envio = request.POST.get('fecha_envio')
        hora_estimada = request.POST.get('hora_estimada')
        descripcion = request.POST.get('descripcion')
        direccion = request.POST.get('direccion_entrega')
        notas = request.POST.get('notas')
        
        # Obtener productos seleccionados
        productos_ids = request.POST.getlist('productos')
        cantidades = request.POST.getlist('cantidades')
        
        if cliente_id and chofer_id and fecha_envio and hora_estimada:
            try:
                cliente = Cliente.objects.get(id=cliente_id)
                chofer = Chofer.objects.get(id=chofer_id)
                
                # Crear el envío
                envio = Envio.objects.create(
                    cliente=cliente,
                    chofer=chofer,
                    fecha_envio=fecha_envio,
                    hora_estimada=hora_estimada,
                    descripcion=descripcion or '',
                    direccion_entrega=direccion or cliente.direccion or '',
                    notas=notas
                )
                
                # Agregar productos al envío
                for prod_id, cant in zip(productos_ids, cantidades):
                    if prod_id and cant:
                        producto = Producto.objects.get(id=prod_id)
                        DetalleEnvio.objects.create(
                            envio=envio,
                            producto=producto,
                            cantidad=int(cant)
                        )
                
                messages.success(request, f'Envío #{envio.id} creado correctamente')
                return redirect('lista_envios')
                
            except Exception as e:
                messages.error(request, f'Error al crear envío: {str(e)}')
        else:
            messages.error(request, 'Complete todos los campos obligatorios')
    
    clientes = Cliente.objects.all().order_by('nombre_completo')
    choferes = Chofer.objects.filter(activo=True).order_by('nombre_completo')
    productos = Producto.objects.all().order_by('nombre')
    
    return render(request, 'envios/crear_envio.html', {
        'clientes': clientes,
        'choferes': choferes,
        'productos': productos,
        'fecha_hoy': date.today()
    })


def detalle_envio(request, envio_id):
    """Ver detalles de un envío específico"""
    envio = get_object_or_404(Envio, id=envio_id)
    detalles = envio.detalles.select_related('producto').all()
    
    return render(request, 'envios/detalle_envio.html', {
        'envio': envio,
        'detalles': detalles
    })


def actualizar_estado_envio(request, envio_id):
    """Actualizar el estado de un envío"""
    envio = get_object_or_404(Envio, id=envio_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado in dict(Envio.ESTADO_CHOICES):
            envio.estado = nuevo_estado
            
            # Si se marca como entregado, registrar hora
            if nuevo_estado == 'entregado' and not envio.hora_real_entrega:
                envio.hora_real_entrega = timezone.now()
            
            envio.save()
            messages.success(request, f'Estado actualizado a "{envio.get_estado_display()}"')
        else:
            messages.error(request, 'Estado inválido')
        
        return redirect('detalle_envio', envio_id=envio_id)
    
    return render(request, 'envios/actualizar_estado.html', {
        'envio': envio,
        'estados': Envio.ESTADO_CHOICES
    })


def programa_dia(request):
    """Vista del programa diario de envíos por chofer"""
    fecha = request.GET.get('fecha', date.today())
    
    envios = Envio.objects.filter(fecha_envio=fecha).select_related(
        'cliente', 'chofer'
    ).prefetch_related('detalles__producto').order_by('chofer', 'hora_estimada')
    
    # Agrupar por chofer
    envios_por_chofer = {}
    for envio in envios:
        chofer_nombre = envio.chofer.nombre_completo if envio.chofer else "Sin Asignar"
        if chofer_nombre not in envios_por_chofer:
            envios_por_chofer[chofer_nombre] = []
        envios_por_chofer[chofer_nombre].append(envio)
    
    return render(request, 'envios/programa_dia.html', {
        'envios_por_chofer': envios_por_chofer,
        'fecha': fecha
    })
