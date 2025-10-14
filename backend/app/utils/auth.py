"""Authentication utilities for token generation and refresh.

These helpers wrap flask-jwt-extended functions to provide
simple interfaces for mobile clients.
"""

from flask_jwt_extended import create_access_token, create_refresh_token


def generate_tokens(identity: str) -> dict:
    """Generate access and refresh tokens for a given identity."""
    return {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
    }


def token_refresh(identity: str) -> str:
    """Generate a new access token for a given identity.

    Use this in a refresh endpoint protected with @jwt_required(refresh=True),
    where identity is obtained via get_jwt_identity().
    """
    return create_access_token(identity=identity)