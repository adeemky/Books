from django.contrib import admin
from .models import User, Author, Book, Review, Category

# Register your models here.

admin.site.register(User)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Review)
