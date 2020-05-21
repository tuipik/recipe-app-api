from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")


def create_user(**param):
    return get_user_model().objects.create_user(**param)


class PublicUserApiTests(TestCase):
    """Test the user API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            "email": "test@testemail.com",
            "password": "testpass",
            "name": "Test Name",
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", response.data)

    def test_user_exists(self):
        """Test creating user already exists fails"""
        payload = {
            "email": "test@testemail.com",
            "password": "testpass",
            "name": "Test",
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test password must be more than 5 characters"""
        payload = {
            "email": "test@testemail.com",
            "password": "pw",
            "name": "Test",
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that token is created for user"""
        payload = {
            "email": "test@testemail.com",
            "password": "testpass",
            "name": "Test",
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email="test@testemail.com", password="testpass")
        payload = {
            "email": "test@testemail.com",
            "password": "wrongpass",
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {
            "email": "test@testemail.com",
            "password": "testpass",
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        response = self.client.post(
            TOKEN_URL, {"email": "test@testemail.com", "password": ""}
        )

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
