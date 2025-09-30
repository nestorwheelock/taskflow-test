import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

User = get_user_model()


class UserEdgeCaseTests(TestCase):
    """Test edge cases and error handling for User model."""

    def test_email_case_insensitive_uniqueness(self):
        """Test that email uniqueness is case-insensitive."""
        User.objects.create_user(
            email='Test@Example.com',
            password='TestPass123!'
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',  # Different case
                password='AnotherPass123!'
            )

    def test_whitespace_in_email_is_normalized(self):
        """Test that whitespace in email is handled properly."""
        user = User.objects.create_user(
            email='  test@example.com  ',
            password='TestPass123!'
        )

        # Email should be normalized (trimmed)
        self.assertEqual(user.email, 'test@example.com')

    def test_empty_names_handle_gracefully(self):
        """Test that empty first_name and last_name are handled properly."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='',
            last_name=''
        )

        self.assertEqual(user.get_full_name(), 'test@example.com')
        self.assertEqual(user.get_short_name(), 'test@example.com')

    def test_very_long_names_are_truncated(self):
        """Test that very long names are handled properly."""
        very_long_name = 'A' * 50  # Longer than max_length=30

        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name=very_long_name,
            last_name=very_long_name
        )

        # Names should be truncated to 30 characters
        self.assertEqual(len(user.first_name), 30)
        self.assertEqual(len(user.last_name), 30)

    def test_special_characters_in_names(self):
        """Test that special characters in names are handled."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name="Jean-François",
            last_name="O'Connor"
        )

        self.assertEqual(user.first_name, "Jean-François")
        self.assertEqual(user.last_name, "O'Connor")
        self.assertEqual(user.get_full_name(), "Jean-François O'Connor")

    def test_unicode_characters_in_names(self):
        """Test that Unicode characters in names are handled."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name="山田",
            last_name="太郎"
        )

        self.assertEqual(user.first_name, "山田")
        self.assertEqual(user.last_name, "太郎")
        self.assertEqual(user.get_full_name(), "山田 太郎")

    def test_none_values_are_handled(self):
        """Test that None values don't break the model."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )

        # These should not raise exceptions
        user.first_name = None
        user.last_name = None

        # Should handle None gracefully
        with transaction.atomic():
            user.save()

    def test_invalid_email_formats(self):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            'not-an-email',
            '@example.com',
            'test@',
            'test..test@example.com',
            'test@example',
        ]

        for invalid_email in invalid_emails:
            with self.subTest(email=invalid_email):
                with self.assertRaises((ValidationError, IntegrityError)):
                    user = User(
                        email=invalid_email,
                        password='TestPass123!'
                    )
                    user.full_clean()  # Trigger validation