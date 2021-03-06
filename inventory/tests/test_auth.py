import factory
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from inventory.tests.factories import UserFactory


class TokenAuthenticationTest(APITestCase):
    def setUp(self):
        """
        Create an user with a token and a client with the token.
        """
        password = factory.Faker('pystr', min_chars=8, max_chars=16)
        self.user = UserFactory.create(password=password)
        self.token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))

    def test_api_with_valid_token(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_without_token(self):
        self.client.credentials()
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            str(response.data['detail']),
            "Authentication credentials were not provided.",
        )

    def test_api_with_invalid_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + str(factory.Faker('pystr'))
        )
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
