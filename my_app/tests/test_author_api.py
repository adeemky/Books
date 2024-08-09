import datetime
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import Author

def create_user():
    return get_user_model().objects.create_user(
        username="testuser",
        email="test@user.com",
        password="passtestuser"
    )

def create_author(user, **params):
    default = {
        "name": "Test Author",
        "date_of_birth": "1965-09-12",
        "country": "Test Country",
    }

    default.update(**params)

    return Author.objects.create(user=user, **default)


# Non-SuperUser Tests
class AuthorApiPublicTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_authors(self):
        res = self.client.get(reverse("myapp:author-list"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_author_fails(self):
        author = {"name": "Test Author"}

        res = self.client.post(reverse("myapp:author-list"), author, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_author_fails(self):
        user = create_user()
        author = create_author(user=user, name="Test Name")


        payload = {
            "name": "Updated Author",
        }

        res = self.client.patch(reverse("myapp:author-detail", args=[author.id]), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

# Authaurized/Superuser Tests
class AuthorApiAdminTest(APITestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            username="testsuperuser",
            email="test@superuser.com",
            password="superuserpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.superuser)

    def test_create_author(self):
        author = {
            "name": "Test Author",
            "date_of_birth": "1966-03-14",
            "country": "Test Country",
        }

        res = self.client.post(reverse("myapp:author-list"), author, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], author["name"])
        self.assertEqual(res.data["date_of_birth"], author["date_of_birth"])
        self.assertEqual(res.data["country"], author["country"])

    def test_partial_update_author(self):
        name = "Paulo Coelho"
        date_of_birth = datetime.date(1958, 11, 25)
        author = create_author(
            user=self.superuser,
            name=name,
            date_of_birth=date_of_birth,
            country="Uruguay",
        )

        payload = {
            "country": "Bresil"
        }

        res = self.client.patch(reverse("myapp:author-detail", args=[author.id]), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        author.refresh_from_db()
        self.assertEqual(res.data["country"], payload["country"])
        self.assertEqual(author.name, name)
        author.date_of_birth.strftime('%Y-%m-%d'), date_of_birth

    def test_full_update_author(self):
        author = create_author(
            user=self.superuser,
            name = "George Orwell",
            date_of_birth = datetime.date(1931, 8, 12),
            country = "United Kingdom"
        )

        payload = {
            "name": "Updated Name",
            "date_of_birth": datetime.date(1896, 4, 30),
            "country": "Updated Country"
        }

        res = self.client.put(reverse("myapp:author-detail", args=[author.id]), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        author.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(author, k), v)

    def test_delete_author(self):
        author = create_author(user=self.superuser)

        res = self.client.delete(reverse("myapp:author-detail", args=[author.id]))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Author.objects.filter(id=author.id).exists())


