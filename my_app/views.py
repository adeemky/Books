from .models import Author, Book, Review, Category
from .serializers import AuthorSerializer, BookSerializer, ReviewSerializer, CategorySerializer
from .permissions import IsAdminOrReadOnly, IsReviewUserOrReadOnly

from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import viewsets, generics
from rest_framework.exceptions import ValidationError

from django.db.models import F

# AUTHOR VIEW
class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# CATEGORY VIEW
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]

# BOOK VIEW
class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        category = self.request.query_params.get('category')
        author = self.request.query_params.get('author')
        queryset = self.queryset

        if category:
            queryset = queryset.filter(category=category)
        if author:
            queryset = queryset.filter(author=author)

        return queryset

# REVIEW VIEW
class ReviewsListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        book_id = self.kwargs['book_id']
        return Review.objects.filter(book__id=book_id)

    def perform_create(self, serializer):
        book_id = self.kwargs['book_id']
        book = Book.objects.get(id=book_id)

        user = self.request.user
        review_queryset = Review.objects.filter(book=book, user=user)

        if review_queryset.exists():
            raise ValidationError("You are already reviewed this movie")

        new_rating = serializer.validated_data["rating"]
        Book.objects.filter(pk=book_id).update(
            avg_rating=((F('avg_rating') * F('number_rating')) + new_rating) / (F('number_rating') + 1),
            number_rating=F('number_rating') + 1
        )

        serializer.save(user=user, book=book)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly]

class UserReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Review.objects.filter(user__id=user_id)

