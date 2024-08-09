from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from ..models import Book, Author, Category


def create_user():
    return get_user_model().objects.create_user(
        username="testuser",
        email="test@user.com",
        password="passtestuser"
    )


def create_book(user, **params):
    author = Author.objects.create(
        user=user,
        name="Example Author"
        )

    category = Category.objects.create(
        name="Test Category",
        description="Test Category Description"
    )

    default = {
        "name": "Test Book",
        "description": "Test Book Description",
        "category": category,
        "author": author,
    }

    default.update(**params)

    return Book.objects.create(user=user, **default)


# Unauthaurized/Non-SuperUser Tests
class BookApiPublicTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        res = self.client.get(reverse("myapp:book-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_fails(self):
        user = create_user()
        author = Author.objects.create(
        user=user,
        name="Example Author"
        )

        category = Category.objects.create(
            name="Test Category",
            description="Test Category Description"
        )


        book = {
            "name": "Test Book Name",
            "description": "Test Description",
            "category": category.id,
            "author": author.id
        }

        res = self.client.post(reverse("myapp:book-list"), book, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book_fails(self):
        user = create_user()
        book = create_book(user=user, name="Test Book Name")

        payload = {"name": "Updated Book Name"}

        res = self.client.put(
            reverse("myapp:book-detail", args=[book.id]), payload, format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Authaurized/Superuser Tests
class BookApiAdminTests(APITestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            username="testsuperuser",
            email="test@superuser.com",
            password="superuserpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.superuser)

        self.author = Author.objects.create(user=self.superuser, name="Example Author")
        self.category = Category.objects.create(name="Test Category")

    def test_create_book(self):
        book = {
            # "user":self.superuser.id,
            "name": "Test Book Name",
            "description": "Test Book description",
            "category": self.category.id,
            "author": self.author.id,
        }

        res = self.client.post(reverse("myapp:book-list"), book, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["user"], self.superuser.username)
        self.assertEqual(res.data["name"], book["name"])
        self.assertEqual(res.data["description"], book["description"])
        self.assertEqual(res.data["author"], self.author.id)

    def test_book_partial_update(self):
        book = create_book(
            user=self.superuser,
            name="New Book",
            description="New Book's description",
            category=self.category,
            author=self.author,
        )

        payload = {"description": "Updated description"}

        res = self.client.patch(
            reverse("myapp:book-detail", args=[book.id]), payload, format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()

        self.assertEqual(res.data["description"], payload["description"])
        self.assertEqual(res.data["name"], book.name)
        self.assertEqual(res.data["category"], book.category.id)
        self.assertEqual(res.data["author"], book.author.id)
        self.assertEqual(res.data["user"], self.superuser.username)

    def test_book_full_update(self):
        book = create_book(
            user=self.superuser,
            name="New Book",
            description="New Book's description",
        )

        new_category = Category.objects.create(
            name="New Category",
            description="New Category Description"
        )

        payload = {
            "name": "Updated Name",
            "description": "Updated description",
            "category": new_category.id,
            "author": self.author.id,
        }

        res = self.client.put(
            reverse("myapp:book-detail", args=[book.id]), payload, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()

        self.assertEqual(res.data["name"], payload["name"])
        self.assertEqual(res.data["description"], payload["description"])
        self.assertEqual(res.data["category"], new_category.id)
        self.assertEqual(res.data["author"], payload["author"])

    def test_delete_book(self):
        book = create_book(user=self.superuser)

        res = self.client.delete(reverse("myapp:book-detail", args=[book.id]))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())
