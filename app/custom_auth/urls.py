from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('user/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('registration/', include('dj_rest_auth.registration.urls')),
]
