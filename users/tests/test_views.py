import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationViewTests(APITestCase):
    """Test user registration API endpoint."""

    def setUp(self):
        self.registration_url = reverse('auth:register')
        self.valid_registration_data = {
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_registration_with_valid_data_returns_201(self):
        """Test that valid registration data creates user and returns 201."""
        response = self.client.post(
            self.registration_url,
            self.valid_registration_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        # Verify user was created
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')

    def test_user_registration_with_invalid_data_returns_400(self):
        """Test that invalid registration data returns 400 with errors."""
        invalid_data = {
            'email': 'invalid-email',
            'password': 'weak',
            'password_confirm': 'different',
            'first_name': '',
            'last_name': ''
        }

        response = self.client.post(
            self.registration_url,
            invalid_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)

    def test_user_registration_with_existing_email_returns_400(self):
        """Test that registration with existing email returns 400."""
        # Create existing user
        User.objects.create_user(
            email='existing@example.com',
            password='ExistingPass123!'
        )

        duplicate_data = self.valid_registration_data.copy()
        duplicate_data['email'] = 'existing@example.com'

        response = self.client.post(
            self.registration_url,
            duplicate_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserLoginViewTests(APITestCase):
    """Test user login API endpoint."""

    def setUp(self):
        self.login_url = reverse('auth:login')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )

    def test_user_login_with_valid_credentials_returns_200_and_tokens(self):
        """Test that valid login returns 200 with JWT tokens."""
        login_data = {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }

        response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')

    def test_user_login_with_invalid_credentials_returns_400(self):
        """Test that invalid login credentials return 400."""
        invalid_data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword123!'
        }

        response = self.client.post(
            self.login_url,
            invalid_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_user_login_with_nonexistent_user_returns_400(self):
        """Test that login with nonexistent user returns 400."""
        invalid_data = {
            'email': 'nonexistent@example.com',
            'password': 'TestPass123!'
        }

        response = self.client.post(
            self.login_url,
            invalid_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_user_login_with_missing_fields_returns_400(self):
        """Test that login with missing fields returns 400."""
        test_cases = [
            {'email': 'testuser@example.com'},  # Missing password
            {'password': 'TestPass123!'},       # Missing email
            {}                                  # Missing both
        ]

        for invalid_data in test_cases:
            with self.subTest(data=invalid_data):
                response = self.client.post(
                    self.login_url,
                    invalid_data,
                    format='json'
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileViewTests(APITestCase):
    """Test user profile API endpoints."""

    def setUp(self):
        self.profile_url = reverse('auth:profile')
        self.user = User.objects.create_user(
            email='profileuser@example.com',
            password='TestPass123!',
            first_name='Profile',
            last_name='User'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_get_profile_with_authentication_returns_200(self):
        """Test that authenticated GET request returns user profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profileuser@example.com')
        self.assertEqual(response.data['first_name'], 'Profile')
        self.assertEqual(response.data['last_name'], 'User')
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)

    def test_get_profile_without_authentication_returns_401(self):
        """Test that unauthenticated GET request returns 401."""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_with_valid_data_returns_200(self):
        """Test that authenticated PUT request updates profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        update_data = {
            'email': 'profileuser@example.com',  # Include required field for PUT
            'first_name': 'Updated',
            'last_name': 'Name'
        }

        response = self.client.put(
            self.profile_url,
            update_data,
            format='json'
        )

        if response.status_code != status.HTTP_200_OK:
            print("Response errors:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        self.assertEqual(response.data['email'], 'profileuser@example.com')  # Unchanged

        # Verify database was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')

    def test_update_profile_without_authentication_returns_401(self):
        """Test that unauthenticated PUT request returns 401."""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }

        response = self.client.put(
            self.profile_url,
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_with_invalid_email_returns_400(self):
        """Test that profile update with invalid email returns 400."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create another user to test uniqueness
        User.objects.create_user(
            email='other@example.com',
            password='TestPass123!'
        )

        update_data = {
            'email': 'other@example.com'  # Try to use existing email
        }

        response = self.client.put(
            self.profile_url,
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_partial_profile_update_works_correctly(self):
        """Test that PATCH request for partial update works."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        update_data = {
            'first_name': 'PartialUpdate'
        }

        response = self.client.patch(
            self.profile_url,
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'PartialUpdate')
        self.assertEqual(response.data['last_name'], 'User')  # Unchanged


class TokenRefreshViewTests(APITestCase):
    """Test JWT token refresh endpoint."""

    def setUp(self):
        self.refresh_url = reverse('auth:refresh')
        self.user = User.objects.create_user(
            email='refreshuser@example.com',
            password='TestPass123!'
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_token_refresh_with_valid_token_returns_200(self):
        """Test that valid refresh token returns new access token."""
        refresh_data = {
            'refresh': str(self.refresh)
        }

        response = self.client.post(
            self.refresh_url,
            refresh_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_with_invalid_token_returns_401(self):
        """Test that invalid refresh token returns 401."""
        refresh_data = {
            'refresh': 'invalid.token.here'
        }

        response = self.client.post(
            self.refresh_url,
            refresh_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_without_token_returns_400(self):
        """Test that missing refresh token returns 400."""
        response = self.client.post(
            self.refresh_url,
            {},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)