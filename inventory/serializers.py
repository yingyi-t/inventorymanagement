from django.db.models import fields
from rest_framework import serializers
from inventory.models import Store, MaterialStock, Material, MaterialQuantity, Product
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class MaterialStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialStock
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


class MaterialQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialQuantity
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
