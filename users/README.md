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

## Serializers

### UserRegistrationSerializer

Handles user registration with comprehensive validation.

**Fields:**
- `email`: EmailField (required, unique validation)
- `password`: CharField (write-only, min 8 chars, strength validation)
- `password_confirm`: CharField (write-only, must match password)
- `first_name`: CharField (optional)
- `last_name`: CharField (optional)

**Validation:**
- Email format and uniqueness validation
- Password strength requirements (8+ chars, uppercase, lowercase, number)
- Password confirmation matching
- Uses Django's built-in password validation

### UserLoginSerializer

Handles user authentication/login validation.

**Fields:**
- `email`: EmailField (required)
- `password`: CharField (required)

**Validation:**
- Authenticates user credentials
- Checks if user account is active
- Returns authenticated user in validated data

### UserProfileSerializer

Handles user profile data serialization and updates.

**Fields:**
- `email`: EmailField (uniqueness validation on update)
- `first_name`: CharField (optional)
- `last_name`: CharField (optional)
- `created_at`: DateTimeField (read-only)
- `updated_at`: DateTimeField (read-only)

**Validation:**
- Email uniqueness validation (excluding current user)
- Profile update validation

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

### Using Serializers

```python
from users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer
)

# User registration
registration_data = {
    'email': 'newuser@example.com',
    'password': 'SecurePass123!',
    'password_confirm': 'SecurePass123!',
    'first_name': 'Jane',
    'last_name': 'Doe'
}
serializer = UserRegistrationSerializer(data=registration_data)
if serializer.is_valid():
    user = serializer.save()

# User login validation
login_data = {
    'email': 'user@example.com',
    'password': 'SecurePass123!'
}
serializer = UserLoginSerializer(data=login_data)
if serializer.is_valid():
    user = serializer.validated_data['user']

# Profile management
serializer = UserProfileSerializer(user)
profile_data = serializer.data

# Profile update
update_data = {'first_name': 'Updated Name'}
serializer = UserProfileSerializer(user, data=update_data, partial=True)
if serializer.is_valid():
    updated_user = serializer.save()
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
- Password strength requirements (8+ chars, mixed case, numbers)
- Automatic timestamp tracking for audit purposes
- Comprehensive validation in serializers

## Testing

The app includes comprehensive tests:

- **Model Tests** (`test_models.py`): Basic user creation and validation
- **Edge Case Tests** (`test_edge_cases.py`): Unicode handling, validation, error cases
- **Serializer Tests** (`test_serializers.py`): Registration, login, and profile serializer validation

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

## API Endpoints

### Authentication Views

#### UserRegistrationView
**POST /api/auth/register** - User registration with JWT token generation

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
}
```

#### UserLoginView
**POST /api/auth/login** - User authentication with JWT token generation

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
}
```

#### UserProfileView
**GET /api/auth/profile** - Get user profile (requires authentication)

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response (200 OK):**
```json
{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

**PUT /api/auth/profile** - Update user profile (requires authentication)

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Request Body:**
```json
{
    "email": "newemail@example.com",
    "first_name": "Updated",
    "last_name": "Name"
}
```

**PATCH /api/auth/profile** - Partial update user profile (requires authentication)

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Request Body:**
```json
{
    "first_name": "Updated"
}
```

#### CustomTokenRefreshView
**POST /api/auth/refresh** - Refresh JWT access token

**Request Body:**
```json
{
    "refresh": "jwt_refresh_token"
}
```

**Response (200 OK):**
```json
{
    "access": "new_jwt_access_token"
}
```

## Testing

The app includes comprehensive tests:

- **Model Tests** (`test_models.py`): Basic user creation and validation (7 tests)
- **Edge Case Tests** (`test_edge_cases.py`): Unicode handling, validation, error cases (8 tests)
- **Serializer Tests** (`test_serializers.py`): Registration, login, and profile serializer validation (15 tests)
- **View Tests** (`test_views.py`): REST API endpoint functionality and authentication (16 tests)

**Total: 46 tests passing**

Run tests with:
```bash
python manage.py test users
```

## API Integration

This authentication system provides:

- JWT token-based authentication for stateless API access
- Complete REST API endpoints for user management
- Comprehensive validation for all user operations
- Secure password handling and email validation
- Token refresh mechanism for long-lived sessions