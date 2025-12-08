import strawberry
from strawberry import auto
from typing import Optional
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import jwt
from datetime import datetime, timedelta
from django.conf import settings


@strawberry.django.type(User)
class UserType:
    id: auto
    username: auto
    email: auto
    first_name: auto
    last_name: auto
    is_active: auto
    date_joined: auto


@strawberry.type
class AuthPayload:
    token: str
    user: UserType


@strawberry.type
class AuthResponse:
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[UserType] = None


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.input
class RegisterInput:
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


def generate_jwt_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


@strawberry.type
class Query:
    @strawberry.field
    def me(self, info) -> Optional[UserType]:
        request = info.context["request"]
        if hasattr(request, 'user') and request.user.is_authenticated:
            return request.user
        return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, input: LoginInput) -> AuthResponse:
        try:
            # Try to find user by email
            user = User.objects.get(email=input.email)
            
            # Authenticate with username and password
            authenticated_user = authenticate(username=user.username, password=input.password)
            
            if authenticated_user:
                token = generate_jwt_token(authenticated_user)
                return AuthResponse(
                    success=True,
                    message="Login successful",
                    token=token,
                    user=authenticated_user
                )
            else:
                return AuthResponse(
                    success=False,
                    message="Invalid credentials"
                )
        except User.DoesNotExist:
            return AuthResponse(
                success=False,
                message="User not found"
            )
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Login failed: {str(e)}"
            )
    
    @strawberry.mutation
    def register(self, input: RegisterInput) -> AuthResponse:
        try:
            # Check if user already exists
            if User.objects.filter(email=input.email).exists():
                return AuthResponse(
                    success=False,
                    message="User with this email already exists"
                )
            
            # Create username from email
            username = input.email.split('@')[0]
            
            # Ensure username is unique
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=input.email,
                password=input.password,
                first_name=input.first_name or '',
                last_name=input.last_name or ''
            )
            
            # Generate token
            token = generate_jwt_token(user)
            
            return AuthResponse(
                success=True,
                message="Registration successful",
                token=token,
                user=user
            )
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Registration failed: {str(e)}"
            )
    
    @strawberry.mutation
    def logout(self) -> AuthResponse:
        # Since JWT is stateless, logout is handled on frontend by removing token
        return AuthResponse(
            success=True,
            message="Logout successful"
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)