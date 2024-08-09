from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import Category

def create_user():
    return get_user_model().objects.create_user(
        username="testuser",
        email="test@user.com",
        password="passtestuser"
    )

def create_category(**params):
    default = {
        "name": "Test Category Name",
        "description": "Test Category Description"
    }

    default.update(**params)

    return Category.objects.create(**default)

# Non-SuperUser Tests
class CategoryApiPublicTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_category(self):
        res = self.client.get(reverse("myapp:category-list"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_category_fails(self):
        category = {"name": "Test Category Name"}

        res = self.client.post(reverse("myapp:category-list"), category, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_category_fails(self):
        category = create_category(name="New Category Name")

        payload = {
            "name": "Updated Category Name"
        }

        res = self.client.patch(reverse("myapp:category-detail", args=[category.id]), payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class CategoryApiAdminTests(APITestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            username="testsuperuser",
            email="test@superuser.com",
            password="superuserpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.superuser)

    def test_create_category(self):
        category = {
            "name": "Test Category Name",
            "description": "Test Category Description"
        }

        res = self.client.post(reverse("myapp:category-list"), category, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], category["name"])
        self.assertEqual(res.data["description"], category["description"])

    def test_partial_update_category(self):
        category = create_category(
            name="New Category Name",
            description="New Category Description"
        )

        payload = {"name": "Updated Category Name"}

        res = self.client.patch(reverse("myapp:category-detail", args=[category.id]), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        category.refresh_from_db()
        self.assertEqual(res.data["name"], payload["name"])
        self.assertEqual(res.data["description"], category.description)

    def test_full_update_category(self):
        category = create_category(
            name="New Category Name",
            description="New Category Description"
        )

        payload = {
            "name": "Updated Category Name",
            "description": "Updated Category Description"
            }

        res = self.client.put(reverse("myapp:category-detail", args=[category.id]), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        category.refresh_from_db()

        self.assertEqual(res.data["name"], payload["name"])
        self.assertEqual(res.data["description"], payload["description"])

    def test_delete_category(self):
        category = create_category()

        res = self.client.delete(reverse("myapp:category-detail", args=[category.id]))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())