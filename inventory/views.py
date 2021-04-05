from django.contrib.auth.models import User

from rest_framework import viewsets, mixins
from rest_framework.response import Response

from inventory.models import Store, MaterialStock, Material, MaterialQuantity, Product
from inventory.serializers import UserSerializer, StoreSerializer, MaterialStockSerializer, \
                                    MaterialSerializer, MaterialQuantitySerializer, ProductSerializer, \
                                    MaterialCapacityInPercentageSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(username=self.request.user.username)


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Store.objects.filter(user=self.request.user)


class MaterialStockViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialStockSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return MaterialStock.objects.filter(store__user=self.request.user)


class MaterialViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Material.objects.filter(material_stocks__store__user=self.request.user)


class MaterialQuantityViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialQuantitySerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return MaterialQuantity.objects.filter(product__store__user=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Product.objects.filter(store__user=self.request.user)


class InventoryViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = MaterialCapacityInPercentageSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return MaterialStock.objects.filter(store__user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        data = {
            "materials": serializer.data,
        }
        return Response(data)