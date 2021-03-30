import factory
from faker import Factory

from django.contrib.auth.models import User
from .models import Store, Product, MaterialQuantity, Material, MaterialStock

faker = Factory.create()

class UserFactory(factory.django.DjangoModelFactory):   
    class Meta:
        model = User
    
    name = faker.name()
    email = faker.email()


class StoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Store

    store_name = faker.name()
    user = factory.SubFactory(UserFactory)


class MaterialStockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterialStock

    store = factory.SubFactory(StoreFactory)
    material = factory.SubFactory(Material)
    max_capacity = faker.pyint(min_value=1, max_value=9999)
    current_capacity = faker.pyint(min_value=1, max_value=max_capacity)
    

class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    name = faker.name()
    price = faker.pydecimal(right_digits=2, positive=True, max_value=9999)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = faker.name()


class MaterialQuantityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterialQuantity
    
    product = factory.SubFactory(ProductFactory)
    ingredient = factory.SubFactory(MaterialFactory)
    quantity = faker.random_int(min=1, max=9999)

