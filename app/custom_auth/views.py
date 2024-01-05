from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.http import Http404

from . import serializers, models


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserDetailView(RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            # Allow staff and admins to view any user's details
            return models.User.objects.get(pk=self.kwargs['pk'])
        elif str(user.pk) == self.kwargs['pk']:
            # Allow users to view their own details
            return user
        else:
            # Otherwise, do not allow access
            raise Http404