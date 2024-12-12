from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth.models import User
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
import logging
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import InvalidToken
from allauth.account.models import EmailAddress
from .serializers import EmailSerializer, VerificationSerializer, CustomTokenObtainPairSerializer
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class VerifyCodeAndCreateUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            # Retrieve the stored data from cache
            cached_data = cache.get(email)

            if cached_data and cached_data['code'] == code:
                # Create the user with the stored email and password
                user = User.objects.create_user(
                    first_name=cached_data['username'],
                    username=email,
                    email=email,
                    password=cached_data['password']  # Hash the password
                )
                user.save()

                # Remove the data from the cache after successful verification
                cache.delete(email)
                return Response({"detail": "User created successfully"}, status=status.HTTP_201_CREATED)
            return Response({"detail": "The code you have entered is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationEmail(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            code = get_random_string(6, allowed_chars='0123456789')

            # Store the email, password (hashed), and code in cache with a TTL of 2 minutes
            cache.set(email, {'username': username, 'password': password, 'code': code}, timeout=120)

            send_mail(
                'Your Verification Code',
                f'Your verification code is {code}',
                'your_email@example.com',  # From email
                [email],  # To email
                fail_silently=False,
            )

            # In production, send the email here. For now, print the code for testing purposes.
            print(f"Verification code for {email}: {code}")

            return Response({"detail": "Verification email sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')

        if refresh_token is None:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            data = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }
            return Response(data, status=status.HTTP_200_OK)
        except InvalidToken:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)



User = get_user_model()

#class GoogleLoginView(SocialLoginView):
#    authentication_classes = []  # Disable authentication, make sure to override `allowed origins` in settings.py
#    adapter_class = GoogleOAuth2Adapter
#    callback_url = "http://localhost:3000"  # Frontend application URL
#    client_class = OAuth2Client

#    def post(self, request, *args, **kwargs):
#        auth_header = request.headers.get('Authorization')
#        if auth_header and auth_header.startswith('Bearer '):
#            access_token = auth_header.split('Bearer ')[1]
#            request.data.update({'access_token': access_token})

        # Extract email from the access token or from Google API call
        # Assuming you've extracted the email already

        # Check if the user already exists
#        try:
            # If you have email in request.data, otherwise fetch from Google API using the access_token
#            email = request.data.get('email')
#            user = User.objects.get(email=email)
#        except User.DoesNotExist:
            # User does not exist, proceed with the original flow to create a new user
#            return super().post(request, *args, **kwargs)

        # If user exists, generate JWT tokens and return them
#        refresh = RefreshToken.for_user(user)
#        jwt_access_token = str(refresh.access_token)
#        jwt_refresh_token = str(refresh)

        # Return the tokens in the response
#        return Response({
#            'access_token': jwt_access_token,
#            'refresh_token': jwt_refresh_token,
#        })

class GoogleLoginView(SocialLoginView):
    authentication_classes = []  # Disable authentication, make sure to override `allowed origins` in settings.py
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/"  # Frontend application URL
    client_class = OAuth2Client


    User = get_user_model()

    def post(self, request, *args, **kwargs):
        print('GoogleLoginView POST called.')
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization header missing or invalid"}, status=400)

        id_token_received = auth_header.split('Bearer ')[1]
        print("ID Token received:", id_token_received)

        try:
            # Verify the ID Token
            id_info = id_token.verify_oauth2_token(
                id_token_received,
                requests.Request(),
                "924096944338-s7cbuedlh7m6md1vgd32tml6oerpiibf.apps.googleusercontent.com"
            )
            print("ID Token verified successfully:", id_info)

           # Ensure the token's audience matches your Google Client ID
            if id_info['aud'] != "924096944338-s7cbuedlh7m6md1vgd32tml6oerpiibf.apps.googleusercontent.com":
                return Response({"error": "Invalid audience"}, status=400)

            # Extract the user's email and other information
            email = id_info.get('email')
            if not email:
                return Response({"error": "Email not found in token"}, status=400)

           # Fetch or create the user
            user, created = User.objects.get_or_create(email=email, defaults={
                "username": id_info.get("given_name", ""),
                "first_name": id_info.get("given_name", ""),
                "last_name": id_info.get("family_name", ""),
            })

           # Update the request data for further processing
            request.data['email'] = email

           # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            jwt_access_token = str(refresh.access_token)
            jwt_refresh_token = str(refresh)
            print(jwt_access_token)
           # Return the tokens
            return Response({
                "access_token": jwt_access_token,
                  "refresh_token": jwt_refresh_token
            }, status=200)

        except ValueError as e:
            print("ID Token verification failed:", e)
            return Response({"error": "Invalid token"}, status=400)

        except Exception as e:
            print("An unexpected error occurred:", e)
            return Response({"error": str(e)}, status=500)

#    def post(self, request, *args, **kwargs):
#        print('heyyy')
#        auth_header = request.headers.get('Authorization')
#        print(auth_header)
#        if auth_header and auth_header.startswith('Bearer '):
#            access_token = auth_header.split('Bearer ')[1]
#            request.data.update({'access_token': access_token})
#        print(request.data)
#        # Call the original post method to handle the authentication
#        response = super().post(request, *args, **kwargs)
 #       print("Response Status Code:", response.status_code)
 #       print("Response Data:", response.data)
  #      # If authentication was successful, generate a JWT token
#        if response.status_code == 200:
 #           Prince('ok')
  #          user = self.user
#            refresh = RefreshToken.for_user(user)
#            jwt_access_token = str(refresh.access_token)
#            jwt_refresh_token = str(refresh)

            # Add the JWT tokens to the response data
#            response.data['access_token'] = jwt_access_token
#            response.data['refresh_token'] = jwt_refresh_token
#            print(response.data)

#        return response

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # If this method is called, the user is authenticated
        return Response({"message": "You are authenticated", "user": request.user.username})

class LogoutView(APIView):
    def post(self, request):
        # Logout the user from the session
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), 'YOUR_GOOGLE_CLIENT_ID')

            # Get user info from token
            email = idinfo['email']
            name = idinfo.get('name', '')
            user_id = idinfo['sub']

            # Authenticate user in Django
            user, created = User.objects.get_or_create(username=user_id, defaults={'email': email, 'first_name': name})

            if created:
                user.set_unusable_password()
                user.save()

            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        except ValueError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
