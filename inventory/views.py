from functools import partial
from django.contrib.auth.models import User
from django.db import IntegrityError

from rest_framework import viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from inventory.models import Store, MaterialStock, Material, MaterialQuantity, Product
from inventory.serializers import UserSerializer, StoreSerializer, MaterialStockSerializer, \
                                    MaterialSerializer, MaterialQuantitySerializer, ProductSerializer, \
                                    MaterialCapacityInPercentageSerializer, ProductCapacitySerializer, \
                                    RestockSerializer, SalesSerializer


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
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        
        if instance.current_capacity != data['current_capacity']:
            raise ValidationError("Current capacity cannot be changed")
        try:
            serializer = self.get_serializer(instance=instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except IntegrityError as e:
            raise ValidationError(e.args[0])
        return Response(serializer.data)


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


class ProductCapacityViewSet(mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    serializer_class = ProductCapacitySerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Store.objects.get(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).products
        serializer = self.get_serializer(queryset, many=True)

        data = {
            "remaining_capacities": serializer.data
        }
        return Response(data)


class RestockViewSet(mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = RestockSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return MaterialStock.objects.filter(store__user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        total_price = self.get_total_price(serializer.data)

        data = {
            "materials": serializer.data,
            "total_price": total_price
        }

        return Response(data)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data['materials']
        except:
            raise ValidationError("No materials given")

        if isinstance(data, list):
            instance = self.get_queryset()
            serializer = self.get_serializer(instance=instance, data=data, many=True, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            final_data = {
                "materials": data,
                "total_price": self.get_total_price(data)
            }
        else:
            raise ValidationError("No materials given")
        
        return Response(final_data)

    def get_total_price(self, materials):
        total_price = 0
        for material in materials:
            price = Material.objects.get(pk=material['material']).price
            total_price += price * material['quantity']
        return round(float(total_price), 2)


class SalesViewSet(mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = SalesSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Store.objects.get(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).products
        serializer = self.get_serializer(queryset, many=True)

        data = {
            "sale": serializer.data
        }
        return Response(data)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data['sale']
        except:
            raise ValidationError("No sale given")
        
        if isinstance(data, list):
            instance = self.get_queryset()
            serializer = self.get_serializer(instance=instance, data=data, many=True, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            final_data = {
                "sale": data,
            }
        else:
            raise ValidationError("No sale given")
        
        return Response(final_data)
