
from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from models import User


def role_required(*allowed_roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):

            # Verify that a valid JWT exists
            verify_jwt_in_request()

            # Get user ID from JWT
            user_id = get_jwt_identity()

            # Find user in database
            try:
                user = User.query.get(int(user_id))
            except (TypeError, ValueError):
                return jsonify({
                    "message": "Invalid user identity"
                }), 401

            if not user:
                return jsonify({
                    "message": "User not found"
                }), 401

            # Reject deactivated accounts
            if not user.is_active:
                return jsonify({
                    "message": "Account is inactive"
                }), 403

            # Check user's role
            if user.role not in allowed_roles:
                return jsonify({
                    "message": "Access denied"
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator
