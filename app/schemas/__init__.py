from .user import UserCreate, UserLogin, UserResponse, Token

# For backward compatibility
User = UserResponse

__all__ = [
    "User", "UserCreate", "UserLogin", "UserResponse", "Token"
]
