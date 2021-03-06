import factory
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import (APIRequestFactory, APITestCase,
                                 force_authenticate)

from inventory import views
from inventory.models import Material, MaterialStock
from inventory.tests.factories import (MaterialFactory, MaterialStockFactory,
                                       StoreFactory, UserFactory)


class RestockViewSetTest(APITestCase):
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
        material1 = MaterialFactory()
        material2 = MaterialFactory()
        material3 = MaterialFactory()
        MaterialStockFactory(
            store=store, material=material1, current_capacity=20, max_capacity=100
        )
        MaterialStockFactory(
            store=store, material=material2, current_capacity=20, max_capacity=100
        )
        MaterialStockFactory(
            store=store, material=material3, current_capacity=20, max_capacity=100
        )

    def test_get_restock(self):
        view = views.RestockViewSet.as_view({'get': 'list'})
        request = self.factory.get('/restock/', format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['materials']), MaterialStock.objects.all().count()
        )
        self.assertEqual(
            response.data, self._get_expected_object(MaterialStock.objects.all())
        )

    def test_post_restock_valid_list(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {
            "materials": [
                {"material": 1, "quantity": 5},
                {"material": 2, "quantity": 5},
            ]
        }
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['materials']), 2)
        self.assertEqual(
            response.data, self._post_expected_object(post_data['materials'])
        )

    def test_post_restock_materials_not_given(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {}
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_restock_no_list_in_materials(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {"materials": {"material": 1, "quantity": "5"}}
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_restock_material_id_not_given(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {"materials": [{"quantity": 5}]}
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_restock_quantity_not_given(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {"materials": [{"material": 1}]}
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_restock_material_id_not_int(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {"materials": [{"material": "5", "quantity": 5}]}
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_restock_material_id_invalid(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {"materials": [{"material": 5, "quantity": 5}]}
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_restock_quantity_not_int(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {"materials": [{"material": 1, "quantity": "5"}]}
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_restock_quantity_not_larger_than_zero(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {"materials": [{"material": 1, "quantity": -4}]}
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_restock_quantity_exceed(self):
        view = views.RestockViewSet.as_view({'post': 'create'})
        post_data = {"materials": [{"material": 1, "quantity": 1000}]}
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _get_expected_object(self, obj):
        materials_list = []
        total_price = 0.0
        for material in obj:
            materials_list.append(
                {
                    "material": material.material.material_id,
                    "quantity": material.max_capacity - material.current_capacity,
                }
            )
            total_price += round(
                float(material.max_capacity - material.current_capacity)
                * float(material.material.price),
                2,
            )

        return_object = {
            "materials": materials_list,
            "total_price": round(total_price, 2),
        }

        return return_object

    def _post_expected_object(self, obj):
        total_price = 0
        for material in obj:
            total_price += round(
                float(Material.objects.get(material_id=material['material']).price)
                * float(material['quantity']),
                2,
            )

        return_object = {"materials": obj, "total_price": round(total_price, 2)}

        return return_object
