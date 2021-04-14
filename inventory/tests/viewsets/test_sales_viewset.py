from faker import Faker

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.authtoken.models import Token

from inventory.tests.factories import MaterialFactory, MaterialStockFactory, ProductFactory, \
                                        StoreFactory, UserFactory, MaterialQuantityFactory
from inventory import views
from inventory.models import MaterialStock


class SalesViewSetTest(APITestCase):
    def setUp(self):
        """
        Create an user with a token and a client with the token. Create a store with products, material quantities,
        materials and material stocks. 
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
        self.material_stock1 = MaterialStockFactory(store=store, material=material1, current_capacity=20)
        self.material_stock2 = MaterialStockFactory(store=store, material=material2, current_capacity=20)
        MaterialQuantityFactory(quantity=2, product=product1, ingredient=material1)
        MaterialQuantityFactory(quantity=2, product=product1, ingredient=material2)
        MaterialQuantityFactory(quantity=2, product=product2, ingredient=material1)
        MaterialQuantityFactory(quantity=2, product=product2, ingredient=material2)

    def test_post_sales_valid_list(self):
        view = views.SalesViewSet.as_view({'post':'create'})
        post_data = {
            "sale": [
                {"product": 1, "quantity": 5},
                {"product": 2, "quantity": 5}]
        }
        request = self.factory.post('/sales/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['sale']), 2)
        self.assertEqual(MaterialStock.objects.get(material=self.material_stock1.material).current_capacity, 0)
        self.assertEqual(MaterialStock.objects.get(material=self.material_stock2.material).current_capacity, 0)

    def test_post_sales_sale_not_given(self):
        view = views.RestockViewSet.as_view({'post':'create'})
        post_data = {}
        request = self.factory.post('/sales/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_sales_no_list_in_sale(self):
        view = views.RestockViewSet.as_view({'post':'create'})
        post_data = {
            "sale": {"product": 1, "quantity": 5}
        }
        request = self.factory.post('/sales/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_sales_product_id_not_given(self):
        view = views.RestockViewSet.as_view({'post':'create'})
        post_data = {
            "sale": [{"quantity": 5}]
        }
        request = self.factory.post('/sales/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_sales_quantity_not_given(self):
        view = views.RestockViewSet.as_view({'post':'create'})
        post_data = {
            "sale": [{"product": 1}]
        }
        request = self.factory.post('/sales/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_sales_product_id_not_int(self):
        view = views.RestockViewSet.as_view({'post':'create'})
        post_data = {
            "sale": [{"product": "1", "quantity": 5}]
        }
        request = self.factory.post('/sales/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_sales_product_id_invalid(self):
        view = views.RestockViewSet.as_view({'post':'create'})
        post_data = {
            "sale": [{"product": 5, "quantity": 5}]
        }
        request = self.factory.post('/restock/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_sales_quantity_not_int(self):
        view = views.RestockViewSet.as_view({'post':'create'})
        post_data = {
            "sale": [{"product": 1, "quantity": "5"}]
        }
        request = self.factory.post('/sales/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_sales_quantity_not_larger_than_zero(self):
        view = views.RestockViewSet.as_view({'post':'create'})
        post_data = {
            "sale": [{"product": 1, "quantity": -5}]
        }
        request = self.factory.post('/sales/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_sales_quantity_exceed(self):
        view = views.RestockViewSet.as_view({'post':'create'})
        post_data = {
            "sale": [
                {"product": 1, "quantity": 10},
                {"product": 2, "quantity": 10}]
        }
        request = self.factory.post('/sales/', post_data, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
