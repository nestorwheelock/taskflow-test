# Users App Documentation

## Overview

The Users app provides custom user authentication for the TaskFlow application using email-based authentication instead of username-based authentication.

## Models

### CustomUser

A custom user model that extends Django's AbstractUser but uses email as the primary authentication field.

**Fields:**
- `email`: EmailField (unique, required) - Primary authentication field
- `first_name`: CharField (optional, max 30 chars)
- `last_name`: CharField (optional, max 30 chars)
- `created_at`: DateTimeField (auto-generated on creation)
- `updated_at`: DateTimeField (auto-updated on modification)
- Inherits: `is_active`, `is_staff`, `is_superuser`, `last_login`, `date_joined` from AbstractUser

**Methods:**
- `get_full_name()`: Returns full name or email if names not provided
- `get_short_name()`: Returns first name or email if not provided
- `__str__()`: Returns email address

### CustomUserManager

Custom manager for the CustomUser model that handles email-based user creation.

**Methods:**
- `create_user(email, password, **extra_fields)`: Creates a regular user
- `create_superuser(email, password, **extra_fields)`: Creates a superuser
- `_create_user(email, password, **extra_fields)`: Internal method for user creation

## Authentication

This app configures Django to use email-based authentication:

- `USERNAME_FIELD = 'email'`
- `REQUIRED_FIELDS = []`
- No username field required

## Usage Examples

### Creating a User

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a regular user
user = User.objects.create_user(
    email='user@example.com',
    password='secure_password',
    first_name='John',
    last_name='Doe'
)

# Create a superuser
admin = User.objects.create_superuser(
    email='admin@example.com',
    password='admin_password'
)
```

### Authentication

```python
from django.contrib.auth import authenticate, login

user = authenticate(
    request,
    username='user@example.com',  # Note: still called 'username' in authenticate()
    password='secure_password'
)

if user is not None:
    login(request, user)
```

## Security Features

- Email uniqueness enforced at database level
- Password hashing using Django's built-in system
- Input validation for email format
- Automatic timestamp tracking for audit purposes

## Testing

The app includes comprehensive tests:

- **Model Tests** (`test_models.py`): Basic user creation and validation
- **Edge Case Tests** (`test_edge_cases.py`): Unicode handling, validation, error cases

Run tests with:
```bash
python manage.py test users
```

## Configuration

Add to Django settings:

```python
INSTALLED_APPS = [
    # ... other apps
    'users',
]

AUTH_USER_MODEL = 'users.CustomUser'
```

## API Integration

This user model integrates with Django REST Framework and JWT authentication:

- JWT tokens use email as the user identifier
- REST API endpoints can authenticate using JWT tokens
- User serialization includes email, names, and timestamps