import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()


class CustomUserModelTests(TestCase):
    """Test suite for custom User model validation and functionality."""

    def test_create_user_with_valid_data_returns_user(self):
        """Test that users can be created with valid data."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='John',
            last_name='Doe'
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_user_with_duplicate_email_raises_error(self):
        """Test that duplicate emails are rejected."""
        User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',
                password='AnotherPass123!'
            )

    def test_create_user_without_email_raises_error(self):
        """Test that users cannot be created without email."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='TestPass123!'
            )

    def test_create_user_without_password_raises_error(self):
        """Test that users cannot be created without password."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test@example.com',
                password=''
            )

    def test_create_superuser_has_staff_permissions(self):
        """Test that superusers are created with proper permissions."""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!'
        )

        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_user_string_representation(self):
        """Test user model string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='John',
            last_name='Doe'
        )

        self.assertEqual(str(user), 'test@example.com')

    def test_user_full_name_property(self):
        """Test user full name property if implemented."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='John',
            last_name='Doe'
        )

        # This test will fail until we implement get_full_name method
        expected_name = 'John Doe'
        self.assertEqual(user.get_full_name(), expected_name)