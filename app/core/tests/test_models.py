from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    def test_create_user_with_email_succefully(self):
        """ Test creating a new user with an email successfully """
        email = "test@test.com"
        password = "test123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_is_normalized(self):
        """Test if the email of a new user is normalized"""
        email = "test@TEST.com"
        password = "test123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, "test@test.com")

    def test_user_invalid_email(self):
        """ Test if a invalid email raises an error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', '123vivalavida')

    def test_create_new_superuser(self):
        """ Test create a new superuser """
        user = get_user_model().objects.create_superuser(
            email="test@TEST.com",
            password="test123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
