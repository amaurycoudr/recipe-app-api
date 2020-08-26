from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="tes@mail.fr", password="azerty"):
    """create a sample user """
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan',
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """ Test the recipe representation """
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Watson',
            time_minutes=5,
            price=5.00,
        )
        self.assertEqual(recipe.title, str(recipe))
