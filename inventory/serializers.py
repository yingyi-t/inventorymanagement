from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from rest_framework import serializers

from inventory.models import Store, MaterialStock, Material, MaterialQuantity, Product


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


class MaterialCapacityInPercentageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialStock
        fields = ['material', 'max_capacity', 'current_capacity', 'percentage_of_capacity',]

    percentage_of_capacity = serializers.SerializerMethodField()

    def get_percentage_of_capacity(self, obj):
        return round(obj.current_capacity / obj.max_capacity * 100.0, 2)


class ProductCapacitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product','quantity']

    product = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    def get_product(self, obj):
        return obj.product_id

    def get_quantity(self, obj):
        return get_product_available_quantity(obj)


class RestockListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        final = []
        need_to_save = []
        
        for item in self.initial_data:
            try:
                existed_material = instance.get(material=item['material'])
            except:
                raise serializers.ValidationError("Material with id of {id} not found in material stock"\
                                                    .format(id=item['material']))

            if not isinstance(item['quantity'], int):
                raise serializers.ValidationError("Quantity is not an integer")
            if item['quantity'] <= 0:
                raise serializers.ValidationError("Quantity is not larger than 0")

            if existed_material.current_capacity + item['quantity'] >= existed_material.max_capacity:
                raise serializers.ValidationError("Current capacity cannot be greater than max capacity")
            
            existed_material.current_capacity = existed_material.current_capacity + item['quantity']
            need_to_save.append(existed_material)

        for save_item in need_to_save:
            save_item.save()
            final.append(existed_material)

        return final


class RestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialStock
        fields = ['material', 'quantity',]
        list_serializer_class = RestockListSerializer
    
    quantity = serializers.SerializerMethodField()

    def get_quantity(self, obj):
        return obj.max_capacity - obj.current_capacity


class SalesListSerializer(serializers.ListSerializer):
    @transaction.atomic
    def update(self, instance, validated_data):
        for item in self.initial_data:
            try:
                current_product = instance.products.all().get(product_id=item["product"])
            except:
                raise serializers.ValidationError("Product with id of {id} not found in store" \
                                                    .format(id=item['product']))
            sold_quantity = item["quantity"]
            if sold_quantity > get_product_available_quantity(current_product):
                raise serializers.ValidationError("Product {id} sold quantity is more than the current available quantity" \
                                                    .format(id=item['product']))
            material_quantities = MaterialQuantity.objects.filter(product=item['product'])
            for material_quantity in material_quantities:
                material_stock_item = instance.material_stocks.get(material=material_quantity.ingredient)
                material_stock_item.current_capacity = material_stock_item.current_capacity \
                                                    - material_quantity.quantity * item['quantity']
                material_stock_item.save()
            
        return self.initial_data


class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product','quantity']
        list_serializer_class = SalesListSerializer

    product = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    def get_product(self, obj):
        return obj.product_id

    def get_quantity(self, obj):
        return get_product_available_quantity(obj)


def get_product_available_quantity(obj):
    material_quantities = MaterialQuantity.objects.filter(product=obj.product_id)
    material_quantities_list = []

    for material_quantity in material_quantities:
        quantity_needed = material_quantity.quantity
        quantity_available = 0
        
        try: 
            stock = obj.store_set.get().material_stocks.get(material=material_quantity.ingredient)
            quantity_available = stock.current_capacity
        except ObjectDoesNotExist:
            pass
    
        material_quantities_list.append(int(quantity_available/quantity_needed))
    
    return min(material_quantities_list)
