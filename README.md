# Books
SCHEMA:
- http://127.0.0.1:8000/api/docs/

ADMIN ACCESS:
- Admin Section: http://127.0.0.1:8000/admin/

ACCOUNTS:
- Registration: http://127.0.0.1:8000/api/user/register/
- Login: http://127.0.0.1:8000/api/user/login/
- Me: http://127.0.0.1:8000/api/user/me/

BOOKS:
- Create Book & Access List: http://127.0.0.1:8000/api/books/
- Access, Update & Destroy Individual Book: http://127.0.0.1:8000/api/books/<int:book_id>/

AUTHORS:
- Create Authors & Acces List: http://127.0.0.1:8000/api/authors/
- Access, Update & Destroy Individual Author: http://127.0.0.1:8000/api/authors/<int:author_id>/

CATEGORIES:
- Create Categories & Acces List: http://127.0.0.1:8000/api/categories/
- Access, Update & Destroy Individual Author: http://127.0.0.1:8000/api/categories/<int:category_id>/

REVIEWS:
- Create, List Review For Specific Book: http://127.0.0.1:8000/api/review/books/<int:book_id>/
- Access, Update & Destroy Individual Review: http://127.0.0.1:8000/api/review/<int:review_id>/
- Access All Reviews For Specific User: http://127.0.0.1:8000/api/review/users/<int:user_id>/

