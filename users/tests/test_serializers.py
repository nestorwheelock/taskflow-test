import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import serializers
from users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer
)

User = get_user_model()


class UserRegistrationSerializerTests(TestCase):
    """Test user registration serializer validation and functionality."""

    def test_valid_registration_data_passes_validation(self):
        """Test that valid registration data passes serializer validation."""
        valid_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        serializer = UserRegistrationSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_password_mismatch_raises_validation_error(self):
        """Test that mismatched passwords raise validation error."""
        invalid_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)

    def test_weak_password_raises_validation_error(self):
        """Test that weak passwords fail validation."""
        weak_passwords = [
            'short',  # Too short
            'alllowercase123',  # No uppercase
            'ALLUPPERCASE123',  # No lowercase
            'NoNumbers!',  # No numbers
            'SimplePass',  # No special chars or numbers
        ]

        for weak_password in weak_passwords:
            with self.subTest(password=weak_password):
                invalid_data = {
                    'email': 'test@example.com',
                    'password': weak_password,
                    'password_confirm': weak_password,
                    'first_name': 'John',
                    'last_name': 'Doe'
                }
                serializer = UserRegistrationSerializer(data=invalid_data)
                self.assertFalse(serializer.is_valid())
                self.assertIn('password', serializer.errors)

    def test_invalid_email_format_raises_validation_error(self):
        """Test that invalid email formats fail validation."""
        invalid_emails = [
            'not-an-email',
            '@example.com',
            'test@',
            'test..test@example.com',
        ]

        for invalid_email in invalid_emails:
            with self.subTest(email=invalid_email):
                invalid_data = {
                    'email': invalid_email,
                    'password': 'TestPass123!',
                    'password_confirm': 'TestPass123!',
                    'first_name': 'John',
                    'last_name': 'Doe'
                }
                serializer = UserRegistrationSerializer(data=invalid_data)
                self.assertFalse(serializer.is_valid())
                self.assertIn('email', serializer.errors)

    def test_duplicate_email_raises_validation_error(self):
        """Test that duplicate emails fail validation."""
        # Create existing user
        User.objects.create_user(
            email='existing@example.com',
            password='ExistingPass123!'
        )

        duplicate_data = {
            'email': 'existing@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        serializer = UserRegistrationSerializer(data=duplicate_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_create_user_with_valid_data_returns_user(self):
        """Test that valid data creates a user successfully."""
        valid_data = {
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
        serializer = UserRegistrationSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Smith')
        self.assertTrue(user.check_password('TestPass123!'))


class UserLoginSerializerTests(TestCase):
    """Test user login serializer validation and functionality."""

    def setUp(self):
        """Set up test user for login tests."""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )

    def test_valid_login_credentials_pass_validation(self):
        """Test that valid login credentials pass validation."""
        valid_data = {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }
        serializer = UserLoginSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_email_fails_validation(self):
        """Test that invalid email fails login validation."""
        invalid_data = {
            'email': 'nonexistent@example.com',
            'password': 'TestPass123!'
        }
        serializer = UserLoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_invalid_password_fails_validation(self):
        """Test that invalid password fails login validation."""
        invalid_data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword123!'
        }
        serializer = UserLoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_empty_fields_fail_validation(self):
        """Test that empty email or password fields fail validation."""
        test_cases = [
            {'email': '', 'password': 'TestPass123!'},
            {'email': 'testuser@example.com', 'password': ''},
            {'email': '', 'password': ''},
        ]

        for invalid_data in test_cases:
            with self.subTest(data=invalid_data):
                serializer = UserLoginSerializer(data=invalid_data)
                self.assertFalse(serializer.is_valid())


class UserProfileSerializerTests(TestCase):
    """Test user profile serializer validation and functionality."""

    def setUp(self):
        """Set up test user for profile tests."""
        self.user = User.objects.create_user(
            email='profileuser@example.com',
            password='TestPass123!',
            first_name='Profile',
            last_name='User'
        )

    def test_profile_serializer_returns_user_data(self):
        """Test that profile serializer returns correct user data."""
        serializer = UserProfileSerializer(self.user)
        data = serializer.data

        self.assertEqual(data['email'], 'profileuser@example.com')
        self.assertEqual(data['first_name'], 'Profile')
        self.assertEqual(data['last_name'], 'User')
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_profile_serializer_excludes_password(self):
        """Test that profile serializer excludes password field."""
        serializer = UserProfileSerializer(self.user)
        data = serializer.data
        self.assertNotIn('password', data)

    def test_profile_update_with_valid_data_succeeds(self):
        """Test that profile update with valid data succeeds."""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        serializer = UserProfileSerializer(self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.email, 'profileuser@example.com')  # Unchanged

    def test_profile_update_email_uniqueness_validation(self):
        """Test that profile update validates email uniqueness."""
        # Create another user
        User.objects.create_user(
            email='other@example.com',
            password='TestPass123!'
        )

        # Try to update profile to existing email
        update_data = {
            'email': 'other@example.com'
        }
        serializer = UserProfileSerializer(self.user, data=update_data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_profile_update_invalid_email_format_fails(self):
        """Test that profile update with invalid email format fails."""
        update_data = {
            'email': 'invalid-email'
        }
        serializer = UserProfileSerializer(self.user, data=update_data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)