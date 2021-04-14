from faker import Faker

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.authtoken.models import Token

from inventory.tests.factories import MaterialFactory, MaterialStockFactory, ProductFactory, \
                                        StoreFactory, UserFactory, MaterialQuantityFactory
from inventory import views
from inventory.models import Product


class ProductCapacityViewSetTest(APITestCase):
    def setUp(self):
        """
        Create an user with a token and a client with the token.
        """        
        password = Faker().pystr(min_chars=8, max_chars=16)
        self.user = UserFactory.create(password=password)
        self.token = Token.objects.create(user=self.user)
        self.factory = APIRequestFactory()

        # set up the data
        product1 = ProductFactory()
        product2 = ProductFactory()
        store = StoreFactory(user=self.user, products=(product1,product2))
        material1 = MaterialFactory()
        material2 = MaterialFactory()
        MaterialStockFactory(store=store, material=material1, current_capacity=20)
        MaterialStockFactory(store=store, material=material2, current_capacity=20)
        MaterialQuantityFactory(quantity=2, product=product1, ingredient=material1)
        MaterialQuantityFactory(quantity=2, product=product1, ingredient=material2)
        MaterialQuantityFactory(quantity=2, product=product2, ingredient=material1)
        MaterialQuantityFactory(quantity=2, product=product2, ingredient=material2)
    
    def test_get_product_capacity(self):
        view = views.ProductCapacityViewSet.as_view({'get': 'list'})
        request = self.factory.get('/product-capacity/', format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['remaining_capacities']), Product.objects.all().count())
        self.assertEqual(response.data, self._get_expected_object(Product.objects.all())) 

    def _get_expected_object(self, obj):
        products_list = []
        for product in obj:
            products_list.append(
                {
                    "product": product.product_id, 
                    "quantity": 10
                })
        
        return_object = {
            "remaining_capacities": products_list
        }

        return return_object
