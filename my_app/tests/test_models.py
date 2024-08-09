from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from ..models import Author, Category, Book, Review

def create_superuser():
    return get_user_model().objects.create_superuser(
        username="testsuperuser",
        email="test@superuser.com",
        password="passsuperuser"
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
        "description": "Test Book description",
        "category": category,
        "author": author
    }

    default.update(**params)

    return Book.objects.create(user=user, **default)


class ModelTests(TestCase):
# USER MODEL TESTS
    def test_create_user(self):
        username = "testuser"
        email = "test@user.com"
        password = "testuser"

        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password
        )

        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ["example1@EXAMPLE.com", "example1@example.com"],
            ["Example2@Example.com", "Example2@example.com"],
            ["EXAMPLE3@EXAMPLE.COM", "EXAMPLE3@example.com"],
            ["example4@example.COM", "example4@example.com"],
        ]

        for i, (email, expected) in enumerate(sample_emails):
            username = f"exampleuser{i + 1}"
            user = get_user_model().objects.create_user(
                username=username,
                email=email,
                password="exampleuser2"
            )
            self.assertEqual(user.email, expected)

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                username="testuser",
                email="",
                password="testuser"
            )

    def test_create_user_without_username(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                username="",
                email="ex@user.com",
                password="testuser"
            )

    def test_username_uniqueness(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="uniqueuser",
            email="unique1@example.com",
            password="password123"
        )

        with self.assertRaises(IntegrityError):
            user_model.objects.create_user(
                username="uniqueuser",
                email="unique2@example.com",
                password="password123",
            )

    def test_email_uniqueness(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="uniqueuser1",
            email="unique@example.com",
            password="password123"
        )

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser("test@example.com", "test123")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

# AUTHOR MODEL TESTS
    def test_create_author(self):
        user = create_superuser()
        author = Author.objects.create(
            user=user,
            name="Test Author",
            date_of_birth="1999-09-21",
            country="Test Country"
        )

        self.assertEqual(str(author), author.name)

# CATEGORY MODEL TESTS
    def test_create_category(self):
        category = Category.objects.create(
            name="Test Category",
            description="Test Category Description"
        )

        self.assertEqual(str(category), category.name)

# BOOK MODEL TESTS
    def test_create_book(self):
        user = create_superuser()
        author = Author.objects.create(
            user=user,
            name="Example Author"
        )

        book = create_book(
            user=user,
            name="Test Book",
            description="Test description",
            author=author
        )

        self.assertEqual(str(book), book.name)

# REVIEW MODEL TEST
    def test_create_review(self):
        user = create_superuser()
        book = create_book(user=user)

        review = Review.objects.create(
            user=user,
            rating=4,
            comment="Test Comment",
            book=book
        )

        review_str = str(review.rating) + " | " + str(review.book) + " | " + str(review.user)

        self.assertEqual(str(review), review_str)