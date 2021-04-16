import factory

from django.contrib.auth.models import User
from ..models import Store, Product, MaterialQuantity, Material, MaterialStock


class UserFactory(factory.django.DjangoModelFactory):   
    class Meta:
        model = User
    
    username = factory.Faker('name')
    email = factory.Faker('email')


class StoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Store

    store_name = factory.Faker('name')
    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing
            return
        
        if extracted:
            for product in extracted:
                self.products.add(product)


class MaterialStockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterialStock

    store = factory.SubFactory(StoreFactory)
    material = factory.SubFactory(Material)
    max_capacity = factory.Faker('pyint', min_value=500, max_value=9999)
    current_capacity = factory.Faker('pyint', min_value=20, max_value=500)
    

class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    name = factory.Faker('name')
    price = factory.Faker('pydecimal', right_digits=2, positive=True, max_value=999)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('name')


class MaterialQuantityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterialQuantity
    
    product = factory.SubFactory(ProductFactory)
    ingredient = factory.SubFactory(MaterialFactory)
    quantity = factory.Faker('pyint', min_value=1, max_value=10)
