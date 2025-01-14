# yourapp/urls.py
from django.urls import path
from .views import TestView, CustomTokenObtainPairView, UserProfileView, GoogleLoginView, LogoutView, ProtectedView, TokenRefreshView, SendVerificationEmail, VerifyCodeAndCreateUser
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('logout/', LogoutView.as_view(), name='account_logout'),
    path("google/", GoogleLoginView.as_view(), name = "google"),
    path('test/', TestView.as_view(), name='test-view'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-login/', SendVerificationEmail.as_view(), name='send_verification_email'),
    path('verify-code/', VerifyCodeAndCreateUser.as_view(), name='verify_code_and_create_user'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
