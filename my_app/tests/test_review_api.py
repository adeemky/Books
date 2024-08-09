from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from ..models import Review, Book, Author, Category
from ..serializers import ReviewSerializer

def create_user():
    return get_user_model().objects.create_user(
        username="testuser1",
        email="test@user1.com",
        password="passtestuser1"
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

# Unauthaurized Tests
class ReviewApiPublicTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_review(self):
        user = create_user()
        book = create_book(user=user)

        res = self.client.get(reverse("myapp:book-reviews", args=[book.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_review_fails(self):
        user = create_user()
        book = create_book(user=user)

        review = {
            "user":user.id,
            "rating": 3,
            "book": book.id
        }

        res = self.client.post(reverse("myapp:book-reviews", args=[book.id]), review, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_fails(self):
        user = create_user()
        book = create_book(user=user)

        review = Review.objects.create(
            user=user,
            rating=4,
            comment="Test Comment",
            book=book
        )

        payload = {
            "comment": "Updated Comment"
        }

        res = self.client.patch(reverse("myapp:review-detail", args=[review.id]), payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

# Authaurized User Tests
class ReviewApiPrivateTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@user.com",
            password="userpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.book = create_book(user=self.user)

    def test_create_review(self):
        review = {
            "user": self.user.id,
            "rating": 4,
            "comment": "Test Comment",
            "book": self.book.id
        }

        res = self.client.post(reverse("myapp:book-reviews", args=[self.book.id]), review, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["user"], self.user.username)
        self.assertEqual(res.data["rating"], review["rating"])
        self.assertEqual(res.data["comment"], review["comment"])
        self.assertEqual(res.data["book"], review["book"])

    def test_review_partial_update(self):
        review = Review.objects.create(
            user=self.user,
            rating=4,
            comment="Test Book Comment",
            book=self.book
        )

        payload = {
            "comment" : "Updated Comment"
        }

        res = self.client.patch(reverse("myapp:review-detail", args=[review.id]), payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()

        self.assertEqual(res.data["comment"], payload["comment"])
        self.assertEqual(res.data["user"], self.user.username)
        self.assertEqual((res.data["rating"]), review.rating)
        self.assertEqual(res.data["book"], self.book.id)

    def test_review_full_update(self):
        review = Review.objects.create(
            user=self.user,
            rating=4,
            comment="Test Book Comment",
            book=self.book
        )

        payload = {
            "user": self.user.id,
            "rating": 3,
            "comment": "Updated Comment",
            'book': self.book.id
        }

        res = self.client.put(reverse("myapp:review-detail", args=[review.id]), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()

        self.assertEqual(res.data["rating"], payload["rating"])
        self.assertEqual(res.data["comment"], payload["comment"])

    def test_delete_book(self):
        review = Review.objects.create(
            user=self.user,
            rating=4,
            book=self.book
        )

        res = self.client.delete(reverse("myapp:review-detail", args=[review.id]))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_list_user_reviews(self):
        review1 = Review.objects.create(
            user=self.user,
            rating=4,
            book=self.book
        )

        review2 = Review.objects.create(
            user=self.user,
            rating=2,
            book=self.book
        )

        res = self.client.get(reverse("myapp:user-reviews", args=[self.user.id]))

        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_other_users_review_fails(self):
        other_user = create_user()

        comment = "Other User's Comment"

        review = Review.objects.create(
            user=other_user,
            rating=5,
            comment=comment,
            book=self.book
        )

        payload = {
            "comment": "Updated Comment"
        }

        res = self.client.patch(reverse("myapp:review-detail", args=[review.id]), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(comment, review.comment)

    def test_delete_other_users_comment_fails(self):
        other_user = create_user()

        review = Review.objects.create(
            user=other_user,
            rating=5,
            book=self.book
        )

        res = self.client.delete(reverse("myapp:review-detail", args=[review.id]))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(id=review.id).exists())