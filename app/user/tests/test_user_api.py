from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the user API(public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Test creating user with valid payload is succesful """
        payload = {
            'email': 'watson@mail.com',
            'password': 'sherlock holmes',
            'name': 'enzodu79',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exist(self):
        """ Test creating user already exists fails"""
        payload = {
            'email': 'watson@mail.com',
            'password': 'sherlock holmes',
            'name': 'enzodu79',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that the password must have more than 5 charaters"""
        payload = {
            'email': 'watson@mail.com',
            'password': 'bite',
            'name': 'enzodu79',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is create for the user"""
        payload = {
            'email': 'watson@mail.com',
            'password': 'sherlock holmes',
            'name': 'enzodu79',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creditantials(self):
        """Test that a token is not create if invalid creditantials
        are given"""
        create_user(email='watson@mail.com',
                    password='sherlock holmes',
                    name='enzodu79')
        payload = {
            'email': 'watson@mail.com',
            'password': 'holmes',
            'name': 'enzodu79',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that a token is not create if user doesn't exist"""
        payload = {
            'email': 'watson@mail.com',
            'password': 'holmes',
            'name': 'enzodu79',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(
            TOKEN_URL, {'email': 'test@mail.com', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """test that authentication required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PriavetUserApiTests(TestCase):
    """Test Api requests that require authentification"""

    def setUp(self):
        self.user = create_user(
            email='test@mail.fr',
            password='password',
            name='watson'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in used"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating profile for authenticated user """
        payload = {'password': 'heolmes',
                   'name': 'enzodu79', }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(self.user.name, payload['name'])