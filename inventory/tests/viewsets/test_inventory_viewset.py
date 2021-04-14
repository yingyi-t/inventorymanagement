from faker import Faker

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.authtoken.models import Token

from inventory.tests.factories import MaterialFactory, MaterialStockFactory, StoreFactory, UserFactory
from inventory import views
from inventory.models import MaterialStock


class InventoryViewSetTest(APITestCase):
    def setUp(self):
        """
        Create an user with a token and a client with the token. Create a store with materials and material stocks. 
        """        
        password = Faker().pystr(min_chars=8, max_chars=16)
        self.user = UserFactory.create(password=password)
        self.token = Token.objects.create(user=self.user)
        self.factory = APIRequestFactory()

        # set up the data
        store = StoreFactory(user=self.user)
        material1 = MaterialFactory()
        material2 = MaterialFactory()
        material3 = MaterialFactory()
        MaterialStockFactory(store=store, material=material1)
        MaterialStockFactory(store=store, material=material2)
        MaterialStockFactory(store=store, material=material3)

    def test_get_inventory(self):
        view = views.InventoryViewSet.as_view({'get': 'list'})
        request = self.factory.get('/inventory/', format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['materials']), MaterialStock.objects.all().count())       
        self.assertEqual(response.data, self._get_expected_object(MaterialStock.objects.all()))

    def _get_expected_object(self, obj):
        materials_list = []
        for material in obj:
            materials_list.append(
                {
                    "material": material.material.material_id, 
                    "max_capacity": material.max_capacity,
                    "current_capacity": material.current_capacity,
                    "percentage_of_capacity": round(material.current_capacity / material.max_capacity * 100.0, 2)
                })

        return_object = {
            "materials": materials_list
        }

        return return_object
