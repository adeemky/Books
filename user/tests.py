from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        new_user = {
            "username": "testnewuser",
            "email": "newuser@email.com",
            "name": "New User",
            "password": "newuserpass",
            "password2": "newuserpass",
        }

        res = self.client.post(reverse("user:register"), new_user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(username=new_user["username"])
        self.assertTrue(user.check_password(new_user["password"]))
        self.assertEqual(res.data["email"], new_user["email"])
        self.assertNotIn("password", res.data)

    def test_register_user_with_existing_username(self):
        create_user(
            username="testuser",
            email="testuser@email.com",
            password="newuserpass"
        )

        new_user = {
            "username": "testuser",
            "email": "newuser@email.com",
            "password": "newuserpass",
            "password2": "newuserpass",
        }

        res = self.client.post(reverse("user:register"), new_user)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_existing_email(self):
        create_user(
            username="testuser",
            email="testuser@email.com",
            password="newuserpass"
        )

        new_user = {
            "username": "testnewuser",
            "email": "testuser@email.com",
            "password": "newuserpass",
            "password2": "newuserpass",
        }

        res = self.client.post(reverse("user:register"), new_user)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_missmatched_passwords(self):
        new_user = {
            "username": "testnewuser",
            "email": "newuser@email.com",
            "password": "correctpass",
            "password2": "incorrectpass",
        }

        res = self.client.post(reverse("user:register"), new_user)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=new_user["username"]).exists()
        self.assertFalse(user_exists)

    def test_register_user_with_short_password(self):
        new_user = {
            "username": "testnewuser",
            "email": "newuser@email.com",
            "password": "short",
            "password2": "short",
        }

        res = self.client.post(reverse("user:register"), new_user)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=new_user["username"]).exists()
        self.assertFalse(user_exists)

# LOGIN TESTS
    def test_login(self):
        create_user(
            username="testuser",
            email="testuser@email.com",
            name="Test User",
            password="newuserpass"
        )

        credentials = {
            "username": "testuser",
            "email": "testuser@email.com",
            "password": "newuserpass",
            "password2": "newuserpass"
        }

        res = self.client.post(reverse("user:login"), credentials)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_with_bad_credentials(self):
        create_user(
            username="testuser",
            email="testuser@email.com",
            password="newuserpass"
        )

        credentials = {
            "username": "testuser",
            "email": "testuser@email.com",
            "password": "badpass",
            "password2": "badpass"
        }

        res = self.client.post(reverse("user:register"), credentials)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthaurized(self):
        res = self.client.get(reverse("user:me"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserTests(TestCase):
    def setUp(self):
        self.user = create_user(
            username="testuser",
            email="testuser@email.com",
            name="Test User",
            password="newuserpass"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_retrieve_profile(self):
        res = self.client.get(reverse("user:me"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "username": self.user.username,
            "email": self.user.email,
            "name": self.user.name
        })

    def test_update_user(self):
        payload = {
            "username": "updatedusername",
            "password": "updatedpassword",
            "password2": "updatedpassword",
        }

        res = self.client.patch(reverse("user:me"), payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
        self.assertEqual(self.user.email, "testuser@email.com")
        self.assertEqual(self.user.name, "Test User")
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_me_not_allowed(self):
        res = self.client.post(reverse("user:me"), {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)