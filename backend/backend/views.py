from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Destinos, Carrito, Nosotros, User, MetodoPago, Profile
from .serializers import (
    DestinosSerializer, 
    MetodoPagoSerializer, 
    CarritoSerializer, 
    NosotrosSerializer, 
    ProfileSerializer,
    RegisterSerializer, 
    LoginSerializer
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import logging
from django.shortcuts import render
from rest_framework import serializers

class MetodoPagoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer

#########################################
# Nosotros
#########################################

logger = logging.getLogger(__name__)

class NosotrosViewSet(viewsets.ModelViewSet):
    queryset = Nosotros.objects.all()
    serializer_class = NosotrosSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        logger.debug('Creating a new Nosotros entry')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.debug(f'Nosotros created successfully: {serializer.data}')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        logger.debug(f'Updating Nosotros with id: {instance.id_nosotros}')
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        logger.debug(f'Nosotros updated successfully: {serializer.data}')
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.debug(f'Deleting Nosotros with id: {instance.id_nosotros}')
        self.perform_destroy(instance)
        logger.debug('Nosotros deleted successfully')
        return Response(status=status.HTTP_204_NO_CONTENT)

###########################
## Destinos
###########################

class DestinosViewSet(viewsets.ModelViewSet):
    queryset = Destinos.objects.all()
    serializer_class = DestinosSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        logger.debug(f'Updating Destino with id: {instance.id_destino}')
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        logger.debug(f'Destino updated successfully: {serializer.data}')
        return Response(serializer.data)

#############################################
####### Carrito
#############################################

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer

    @action(detail=True, methods=['put'])
    def actualizar_cantidad(self, request, pk=None):
        try:
            carrito_item = self.get_object()
            nueva_cantidad = request.data.get('cantidad')

            if not nueva_cantidad or int(nueva_cantidad) < 1:
                return Response({'error': 'Cantidad inválida'}, status=status.HTTP_400_BAD_REQUEST)

            carrito_item.cantidad = int(nueva_cantidad)
            carrito_item.save()
            return Response(CarritoSerializer(carrito_item).data)
        except Carrito.DoesNotExist:
            return Response({'error': 'Carrito item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error al actualizar la cantidad: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_al_carrito(request):
    try:
        id_destino = request.data.get('id_destino')

        if not id_destino:
            return Response({'error': 'id_destino is required'}, status=status.HTTP_400_BAD_REQUEST)

        destino = Destinos.objects.get(pk=id_destino)
        metodo_pago_predeterminado = MetodoPago.objects.first()

        carrito_item, created = Carrito.objects.get_or_create(
            user=request.user,
            id_destino=destino,
            defaults={'cantidad': 1, 'id_metodoPago': metodo_pago_predeterminado}
        )
        if not created:
            carrito_item.cantidad += 1
            carrito_item.save()

        serializer = CarritoSerializer(carrito_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Destinos.DoesNotExist:
        return Response({'error': 'Destino not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_carrito(request):
    try:
        carrito_items = Carrito.objects.filter(user=request.user)
        serializer = CarritoSerializer(carrito_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_item_carrito(request, id):
    try:
        carrito_item = Carrito.objects.get(pk=id, user=request.user)
        carrito_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Carrito.DoesNotExist:
        return Response({'error': 'Carrito item not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def actualizar_fecha_salida(request, id):
    try:
        carrito_item = Carrito.objects.get(pk=id)
    except Carrito.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = request.data
    fecha_salida = data.get('fecha_salida')
    if fecha_salida:
        carrito_item.fecha_salida = fecha_salida
        carrito_item.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Fecha de salida no proporcionada"})

#################################
### Dashboard
#################################

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_compras(request):
    compras = Carrito.objects.filter(user=request.user)
    serializer = CarritoSerializer(compras, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_perfil_usuario(request):
    try:
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        return Response({'error': 'Perfil no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

##############################################

@api_view(['POST'])
def checkout(request):
    try:
        carrito_items = Carrito.objects.filter(user=request.user)
        metodo_pago = MetodoPago.objects.get(id_metodoPago=request.data['metodo_pago'])

        if not carrito_items.exists():
            return Response({'error': 'El carrito está vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        for item in carrito_items:
            item.estado = 'comprado'
            item.save()

        return Response({'message': 'Compra realizada con éxito.'}, status=status.HTTP_200_OK)
    except MetodoPago.DoesNotExist:
        return Response({'error': 'Método de pago no válido.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_refresh(request):
    serializer = TokenRefreshView().get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)

# Perfiles de Usuario

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profile_api_view(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()
        profiles_serializer = ProfileSerializer(profiles, many=True)
        return Response(profiles_serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        profile_serializer = ProfileSerializer(data=request.data)
        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(profile_serializer.data, status=status.HTTP_201_CREATED)
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_usuario_autenticado(request):
    try:
        profile = Profile.objects.get(user=request.user)
        profile_serializer = ProfileSerializer(profile)
        return Response(profile_serializer.data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        return Response({'error': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def profile_detail_api_view(request, pk=None):
    profile = Profile.objects.filter(id=pk).first()
    if profile:
        if request.method == 'GET':
            profile_serializer = ProfileSerializer(profile)
            return Response(profile_serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PUT':
            profile_serializer = ProfileSerializer(profile, data=request.data)
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response(profile_serializer.data, status=status.HTTP_200_OK)
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            profile.delete()
            return Response({'message': 'Perfil eliminado correctamente'}, status=status.HTTP_200_OK)
    return Response({'message': 'No se ha encontrado un perfil con estos datos'}, status=status.HTTP_404_NOT_FOUND)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            register_serializer = self.get_serializer(data=request.data)
            register_serializer.is_valid(raise_exception=True)
            user = register_serializer.save()

            # La señal post_save se encargará de crear el perfil automáticamente
            
            # Autenticar al usuario recién creado
            login_data = {
                'email': request.data['email'],
                'password': request.data['password']
            }
            login_serializer = LoginSerializer(data=login_data)
            login_serializer.is_valid(raise_exception=True)
            user = login_serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)
            
            # Obtener el perfil creado por la señal
            profile = Profile.objects.get(user=user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': ProfileSerializer(profile).data
            }, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profile_api_view(request):
    """
    Lista todos los perfiles o crea uno nuevo
    """
    if request.method == 'GET':
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def profile_detail_api_view(request, pk):
    """
    Obtiene, actualiza o elimina un perfil específico
    """
    try:
        profile = Profile.objects.get(pk=pk)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)