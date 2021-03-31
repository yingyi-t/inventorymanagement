from django.db import models
from django.db.models import CheckConstraint, UniqueConstraint, Q, F, Value
from django.db.models.functions import Concat


class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    store_name = models.CharField(max_length=100, unique=True)
    products = models.ManyToManyField('Product', blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.store_name


class MaterialStock(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='material_stocks')
    material = models.ForeignKey('Material', on_delete=models.CASCADE, related_name='material_stocks')
    max_capacity = models.PositiveIntegerField(default=9999)
    current_capacity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Material Stocks"
        constraints = [CheckConstraint(check=Q(max_capacity__gt=0), name='max capacity >= 0'),
                        CheckConstraint(check=Q(current_capacity__gte=0) & Q(current_capacity__lte=F('max_capacity')), 
                        name='current capacity >= to 0 and <= max capacity'),
                        UniqueConstraint(fields=['store', 'material'], name='unique material stock')]
    
    def __str__(self):
        string = (self.store, self.material)
        return " ".join(str(s) for s in string)


class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        constraints = [CheckConstraint(check=Q(price__gte=0), name='price >= 0')]

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    materials = models.ManyToManyField(Material, through='MaterialQuantity', related_name='products')

    def __str__(self):
        return self.name


class MaterialQuantity(models.Model):
    product = models.ForeignKey('Product', related_name='material_quantities', on_delete=models.CASCADE)
    ingredient = models.ForeignKey('Material', related_name='material_quantities', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name_plural = "Material Quantities"
        constraints = [CheckConstraint(check=Q(quantity__gt=0), name='quantity > 0'),
                        UniqueConstraint(fields=['product', 'ingredient'], name='unique product quantity')]

    def __str__(self):
        string = (self.product, self.ingredient, self.quantity)
        return " ".join(str(s) for s in string)

