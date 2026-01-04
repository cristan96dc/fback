from django.db import models

# Create your models here.
class TipoProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


# ------------------------------
#  MODELO: Producto
# ------------------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)

    cantidad = models.PositiveIntegerField(default=0)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    
    # 👈 NUEVO CAMPO DE ALERTA
    umbral_alerta = models.PositiveIntegerField(
        default=5, # Valor por defecto que el usuario puede cambiar
        verbose_name="Stock Mínimo de Alerta"
    )
    # -------------------------
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ruta = models.CharField(max_length=500)
    
    def __str__(self):
        return f"Imagen {self.id} - {self.producto.nombre}"
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} unidades)"



class Ventas(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    
    # 🚨 CAMBIO CLAVE: Hacer que el CharField sea opcional
    cliente = models.CharField(
        max_length=100, 
        blank=True,  # Permite que el campo se deje vacío en formularios (frontend/Django)
        null=True    # Permite que se guarde un valor NULL en la base de datos (DB)
    )
    
    cantidad = models.PositiveIntegerField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Agregué default=0 por precaución
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # calcular valor total automáticamente
        # Aseguramos que self.producto esté cargado antes de acceder a su valor
        if self.producto_id and self.producto.valor is not None and self.cantidad is not None:
             self.valor_total = self.producto.valor * self.cantidad
        else:
             # Si falta alguno de los datos clave (aunque la vista debería proveerlos), usamos 0
             self.valor_total = 0 
             
        super().save(*args, **kwargs)

    def __str__(self):
        # Muestra 'Sin Cliente' si el campo está vacío/nulo
        nombre_cliente = self.cliente if self.cliente else "Sin Cliente" 
        return f"Venta de {self.cantidad} x {self.producto.nombre} a {nombre_cliente}"

# ------------------------------
#  MODELO: Cliente
# ------------------------------
class Cliente(models.Model):
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre y Apellido")
    nombre_local = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nombre del Local")
    email = models.EmailField(unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre_completo']
    
    def __str__(self):
        if self.nombre_local:
            return f"{self.nombre_completo} - {self.nombre_local}"
        return self.nombre_completo



class Chofer(models.Model):
    """Modelo para gestionar choferes/conductores"""
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=20)
    vehiculo = models.CharField(max_length=100, verbose_name="Vehículo/Patente")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas/Descripción")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Chofer"
        verbose_name_plural = "Choferes"
        ordering = ['nombre_completo']
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.vehiculo}"


class Envio(models.Model):
    """Modelo para gestionar envíos/entregas"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_camino', 'En Camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Relaciones
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    chofer = models.ForeignKey(Chofer, on_delete=models.SET_NULL, null=True, verbose_name="Chofer Asignado")
    
    # Información del envío
    fecha_envio = models.DateField(verbose_name="Fecha de Envío")
    hora_estimada = models.TimeField(verbose_name="Hora Estimada de Entrega")
    descripcion = models.TextField(verbose_name="Descripción del Envío")
    
    # Estado y seguimiento
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    hora_real_entrega = models.DateTimeField(blank=True, null=True, verbose_name="Hora Real de Entrega")
    
    # Información adicional
    direccion_entrega = models.TextField(verbose_name="Dirección de Entrega")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Envío"
        verbose_name_plural = "Envíos"
        ordering = ['-fecha_envio', 'hora_estimada']
    
    def __str__(self):
        return f"Envío {self.id} - {self.cliente.nombre_completo} ({self.fecha_envio})"


class DetalleEnvio(models.Model):
    """Modelo para los productos incluidos en cada envío"""
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    
    class Meta:
        verbose_name = "Detalle de Envío"
        verbose_name_plural = "Detalles de Envíos"
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"