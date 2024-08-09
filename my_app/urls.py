from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, BookViewSet, ReviewsListCreateView, ReviewDetailView, UserReviewsView, CategoryViewSet

router = DefaultRouter()
router.register('authors', AuthorViewSet, basename='author')
router.register('categories', CategoryViewSet, basename='category')
router.register('books', BookViewSet, basename='book')

app_name = 'myapp'

urlpatterns = [
    path('', include(router.urls)),

    path('review/books/<int:book_id>/', ReviewsListCreateView.as_view(), name="book-reviews"),
    path('review/<int:pk>/', ReviewDetailView.as_view(), name="review-detail"),
    path("review/users/<int:user_id>/", UserReviewsView.as_view(), name="user-reviews")
]
