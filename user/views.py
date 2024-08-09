from rest_framework import generics, authentication, permissions
from .serializers import UserSerializer, AuthTokenSerializer, UpdateUserSerializer
from rest_framework.authtoken.views import ObtainAuthToken

# REGISTER USER
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

# RETIEVE UPDATE USER
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateUserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# LOGIN VIEW
class LoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer



