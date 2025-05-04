from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DestinosViewSet, 
    MetodoPagoViewSet, 
    NosotrosViewSet, 
    CarritoViewSet,
    profile_api_view,          # Cambiado de user_api_view
    profile_detail_api_view,   # Cambiado de user_detail_api_view
    obtener_usuario_autenticado, 
    listar_compras, 
    obtener_perfil_usuario, 
    checkout, 
    LoginView, 
    RegisterView, 
    token_refresh, 
    agregar_al_carrito, 
    obtener_carrito, 
    eliminar_item_carrito, 
    actualizar_fecha_salida
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'destinos', DestinosViewSet)
router.register(r'nosotros', NosotrosViewSet)
router.register(r'carrito', CarritoViewSet, basename='carrito')
router.register(r'metodos-pago', MetodoPagoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Perfiles (reemplazan a usuarios)
    path('profiles/', profile_api_view, name='profiles_api'),
    path('profiles/<int:pk>/', profile_detail_api_view, name='profiles_detail_api_view'),
    
    # Autenticación
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', token_refresh, name='token_refresh'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_jwt'),
    
    # Carrito
    path('agregar-al-carrito/', agregar_al_carrito, name='agregar-al-carrito'),
    path('eliminar-item-carrito/<int:id>/', eliminar_item_carrito, name='eliminar-item-carrito'),
    path('carrito/', obtener_carrito, name='obtener_carrito'),
    path('carrito/<int:pk>/actualizar_cantidad/', CarritoViewSet.as_view({'put': 'actualizar_cantidad'}), name='actualizar_cantidad'),
    path('carrito/<int:id>/actualizar_fecha/', actualizar_fecha_salida, name='actualizar_fecha_salida'),
    
    # Otros
    path('checkout/', checkout, name='checkout'),
    path('listar-compras/', listar_compras, name='listar_compras'),
    path('perfil/', obtener_perfil_usuario, name='obtener_perfil'),
    path('user/me/', obtener_usuario_autenticado, name='obtener_usuario_autenticado'),
    
    # Router
    path('api/', include(router.urls)),
]