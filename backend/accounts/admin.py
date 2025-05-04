from django.contrib import admin
from .models import Profile, Destinos, Categorias, MetodoPago, Nosotros, Carrito
from django import forms

# PROFILE DETALLADO
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mail', 'address', 'location', 'telephone', 'user_group')
    search_fields = ('user__username', 'location', 'user__groups__name')
    list_filter = ('user__groups', 'location')

    def user_group(self, obj):
        return " - ".join([t.name for t in obj.user.groups.all().order_by('name')])
    user_group.short_description = 'Grupo'

class DestinosAdmin(admin.ModelAdmin):
    list_display = ('id_destino', 'nombre_Destino', 'descripcion', 'image', 'precio_Destino', 
                    'fecha_salida', 'cantidad_Disponible', 'disponibilidad_display')
    search_fields = ('nombre_Destino', 'descripcion')
    list_filter = ('fecha_salida', 'cantidad_Disponible', 'id_categoria')
    ordering = ('fecha_salida',)
    fields = ('nombre_Destino', 'descripcion', 'image', 'precio_Destino', 'fecha_salida',
              'cantidad_Disponible', 'id_metodoPago', 'id_categoria')

class CategoriasAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombreCategoria')

class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('id_metodoPago', 'nombrePago')

class NosotrosAdmin(admin.ModelAdmin):
    list_display = ('id_nosotros', 'nombre_apellido', 'github', 'linkedin', 'imagen')
    search_fields = ('nombre_apellido', 'github', 'linkedin')

# FORMULARIO PERSONALIZADO PARA CARRITO
class CarritoAdminForm(forms.ModelForm):
    class Meta:
        model = Carrito
        fields = ('user', 'id_destino', 'cantidad', 'id_metodoPago')

class CarritoAdmin(admin.ModelAdmin):
    form = CarritoAdminForm
    list_display = ('id_compra', 'user', 'id_destino', 'cantidad', 'id_metodoPago', 
                   'fecha_creacion', 'total_display', 'cupos_disponibles_display')
    list_filter = ('fecha_creacion', 'id_metodoPago', 'id_destino')
    search_fields = ('user__username', 'id_destino__nombre_Destino')
    readonly_fields = ('fecha_creacion', 'cupos_disponibles_display', 'total_display')
    
    # Campos para la vista de edición
    fieldsets = (
        ('Información Principal', {
            'fields': ('user', 'id_destino', 'cantidad', 'id_metodoPago')
        }),
        ('Información Adicional', {
            'fields': ('fecha_creacion', 'cupos_disponibles_display', 'total_display'),
            'classes': ('collapse',)
        }),
    )

    # Campos para la vista de lista
    list_display_links = ('id_compra', 'user')
    
    def cupos_disponibles_display(self, obj):
        if obj.id_destino:
            return obj.id_destino.cantidad_Disponible
        return "N/A"
    cupos_disponibles_display.short_description = "Cupos Disponibles"

    def total_display(self, obj):
        return f"${obj.total:,.2f}" if obj.total else "N/A"
    total_display.short_description = "Total Reserva"

    def get_fieldsets(self, request, obj=None):
        if obj is None:  # Estamos en la vista de creación
            return (
                ('Información Principal', {
                    'fields': ('user', 'id_destino', 'cantidad', 'id_metodoPago')
                }),
            )
        return super().get_fieldsets(request, obj)

    def save_model(self, request, obj, form, change):
        # Asegurarnos de que se ejecuten las validaciones personalizadas
        obj.full_clean()
        super().save_model(request, obj, form, change)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Destinos, DestinosAdmin)
admin.site.register(Categorias, CategoriasAdmin)
admin.site.register(MetodoPago, MetodoPagoAdmin)
admin.site.register(Nosotros, NosotrosAdmin)
admin.site.register(Carrito, CarritoAdmin)