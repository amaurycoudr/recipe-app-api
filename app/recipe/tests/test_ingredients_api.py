from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredient api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required to retriving ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the authorized user ingredient api """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email='watson@mail.fr',
            password='testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """ test retrieving ingredients"""
        Ingredient.objects.create(user=self.user, name='Potatos')
        Ingredient.objects.create(user=self.user, name='Beaf')
        res = self.client.get(INGREDIENTS_URL)
        ingredient = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """ test that ingredients returned are for authenticated user"""
        user2 = get_user_model().objects.create(email='email2@mail.com',
                                                password='testpass')
        ingredient = Ingredient.objects.create(user=self.user, name='Potatos')
        Ingredient.objects.create(user=user2, name='Beaf')
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient(self):
        """ test creating ingredient"""
        payload = {'name': 'name'}
        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user, name='name').exists()

        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_ingredient_invalid(self):
        """Test creating ingredient invalid"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
