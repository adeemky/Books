from rest_framework import serializers
from .models import Author, Book, Review, Category


# AUTHOR SERIALIZER
class AuthorSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Author
        fields = ["id", "user", "name", "date_of_birth", "country"]
        read_only_fields = ["id"]

# CATEGORY SERIALIZER
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]

# BOOK SERIALIZER
class BookSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    #author = serializers.CharField(source="author.name")
    class Meta:
        model = Book
        fields = ["id", "user", "name", "description", "category", "author", "avg_rating", "number_rating"]
        read_only_fields = ["id"]


# REVIEW SERIALIZER
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "book"]
        read_only_fields = ["id", "book"]
