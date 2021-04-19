import factory
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import (APIRequestFactory, APITestCase,
                                 force_authenticate)

from inventory import views
from inventory.models import MaterialStock
from inventory.tests.factories import (MaterialFactory, MaterialStockFactory,
                                       StoreFactory, UserFactory)


class MaterialStockViewSetTest(APITestCase):
    def setUp(self):
        """
        Create an user with a token and a client with the token. Create a store with materials and material stocks.
        """
        password = factory.Faker('pystr', min_chars=8, max_chars=16)
        self.user = UserFactory.create(password=password)
        self.token = Token.objects.create(user=self.user)
        self.factory = APIRequestFactory()

        # set up the data
        store = StoreFactory(user=self.user)
        material = MaterialFactory()
        self.material_stock = MaterialStockFactory(
            store=store, material=material, current_capacity=20, max_capacity=100
        )

    def test_put_material_stock_max_capacity_valid(self):
        view = views.MaterialStockViewSet.as_view({'put': 'update'})
        put_data = {
            "id": 1,
            "max_capacity": 200,
            "current_capacity": 20,
            "store": 1,
            "material": 1,
        }
        request = self.factory.put('/material-stocks/', put_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            MaterialStock.objects.get(
                material=self.material_stock.material
            ).max_capacity,
            200,
        )

    def test_put_material_stock_current_capacity(self):
        view = views.MaterialStockViewSet.as_view({'put': 'update'})
        put_data = {
            "id": 1,
            "max_capacity": 100,
            "current_capacity": 10,
            "store": 1,
            "material": 1,
        }
        request = self.factory.put('/material-stocks/', put_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        with transaction.atomic():
            response = view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            MaterialStock.objects.get(
                material=self.material_stock.material
            ).current_capacity,
            20,
        )

    def test_put_material_stock_max_capacity_less_than_current_capacity(self):
        view = views.MaterialStockViewSet.as_view({'put': 'update'})
        put_data = {
            "id": 1,
            "max_capacity": 10,
            "current_capacity": 20,
            "store": 1,
            "material": 1,
        }
        request = self.factory.put('/material-stocks/', put_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        with transaction.atomic():
            response = view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            MaterialStock.objects.get(
                material=self.material_stock.material
            ).max_capacity,
            100,
        )
