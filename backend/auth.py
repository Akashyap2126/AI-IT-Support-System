from extensions import limiter

from flask import Blueprint, request

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from datetime import datetime, timedelta
import hashlib

from models import (
    db,
    User,
    SecurityEvent,
    RefreshToken
)

from decorators import role_required


auth_bp = Blueprint("auth", __name__)


# ==========================================
# HASH TOKEN
# ==========================================

def hash_token(token):
    return hashlib.sha256(
        token.encode()
    ).hexdigest()


# ==========================================
# GET RAW BEARER TOKEN
# ==========================================

def get_bearer_token():

    authorization = request.headers.get("Authorization")

    if not authorization:
        return None

    parts = authorization.split(" ", 1)

    if len(parts) != 2:
        return None

    if parts[0].lower() != "bearer":
        return None

    return parts[1]


# ==========================================
# REGISTER
# POST /api/auth/register
# ==========================================

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():

    data = request.get_json()

    if not data:
        return {
            "message": "Request body is required"
        }, 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return {
            "message": "Name, email and password are required"
        }, 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return {
            "message": "Email already registered"
        }, 409

    password_hash = generate_password_hash(password)

    user = User(
        name=name,
        email=email,
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    return {
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }, 201


# ==========================================
# LOGIN
# POST /api/auth/login
# ==========================================

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():

    data = request.get_json()

    if not data:
        return {
            "message": "Request body is required"
        }, 400

    email = data.get("email")
    password = data.get("password")

    ip_address = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    if not email or not password:
        return {
            "message": "Email and password are required"
        }, 400

    user = User.query.filter_by(
        email=email
    ).first()

    # ------------------------------------------
    # USER NOT FOUND
    # ------------------------------------------

    if not user:

        security_event = SecurityEvent(
            user_id=None,
            event_type="LOGIN_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            details=(
                f"Failed login attempt for unknown email: {email}"
            )
        )

        db.session.add(security_event)
        db.session.commit()

        return {
            "message": "Invalid email or password"
        }, 401

    # ------------------------------------------
    # INACTIVE ACCOUNT
    # ------------------------------------------

    if not user.is_active:

        security_event = SecurityEvent(
            user_id=user.id,
            event_type="LOGIN_INACTIVE_ACCOUNT",
            ip_address=ip_address,
            user_agent=user_agent,
            details="Login attempt on inactive account"
        )

        db.session.add(security_event)
        db.session.commit()

        return {
            "message": "User account is inactive"
        }, 403

    # ------------------------------------------
    # WRONG PASSWORD
    # ------------------------------------------

    if not check_password_hash(
        user.password_hash,
        password
    ):

        security_event = SecurityEvent(
            user_id=user.id,
            event_type="LOGIN_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            details="Invalid password"
        )

        db.session.add(security_event)
        db.session.commit()

        return {
            "message": "Invalid email or password"
        }, 401

    # ==========================================
    # CREATE TOKENS
    # ==========================================

    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(minutes=15)
    )

    refresh_token = create_refresh_token(
        identity=str(user.id),
        expires_delta=timedelta(days=30)
    )

    # ==========================================
    # STORE HASHED REFRESH TOKEN
    # ==========================================

    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=30),
        revoked=False
    )

    db.session.add(refresh_token_record)

    # ==========================================
    # SECURITY EVENT
    # ==========================================

    security_event = SecurityEvent(
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        ip_address=ip_address,
        user_agent=user_agent,
        details="User logged in successfully"
    )

    db.session.add(security_event)

    db.session.commit()

    return {
        "message": "Login successful",

        "access_token": access_token,

        "refresh_token": refresh_token,

        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }, 200


# ==========================================
# REFRESH ACCESS TOKEN
# POST /api/auth/refresh
# ==========================================

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    if not user:
        return {
            "message": "User not found"
        }, 404

    if not user.is_active:
        return {
            "message": "User account is inactive"
        }, 403

    # ------------------------------------------
    # GET CURRENT REFRESH TOKEN
    # ------------------------------------------

    raw_token = get_bearer_token()

    if not raw_token:
        return {
            "message": "Refresh token is required"
        }, 401

    token_hash = hash_token(raw_token)

    refresh_record = RefreshToken.query.filter_by(
        user_id=user_id,
        token_hash=token_hash
    ).first()

    if not refresh_record:
        return {
            "message": "Refresh token not recognized"
        }, 401

    # ------------------------------------------
    # CHECK REVOCATION
    # ------------------------------------------

    if refresh_record.revoked:

        security_event = SecurityEvent(
            user_id=user_id,
            event_type="REVOKED_REFRESH_TOKEN_USED",
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            details="Attempted use of a revoked refresh token"
        )

        db.session.add(security_event)
        db.session.commit()

        return {
            "message": "Refresh token has been revoked"
        }, 401

    # ------------------------------------------
    # CHECK DATABASE EXPIRATION
    # ------------------------------------------

    if refresh_record.expires_at <= datetime.utcnow():

        refresh_record.revoked = True

        security_event = SecurityEvent(
            user_id=user_id,
            event_type="EXPIRED_REFRESH_TOKEN_USED",
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            details="Attempted use of an expired refresh token"
        )

        db.session.add(security_event)
        db.session.commit()

        return {
            "message": "Refresh token has expired"
        }, 401

    # ==========================================
    # ROTATE REFRESH TOKEN
    # ==========================================

    refresh_record.revoked = True

    new_access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(minutes=15)
    )

    new_refresh_token = create_refresh_token(
        identity=str(user.id),
        expires_delta=timedelta(days=30)
    )

    new_refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=30),
        revoked=False
    )

    db.session.add(new_refresh_record)

    # ------------------------------------------
    # SECURITY EVENT
    # ------------------------------------------

    security_event = SecurityEvent(
        user_id=user.id,
        event_type="TOKEN_REFRESHED",
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        details="Refresh token rotated successfully"
    )

    db.session.add(security_event)

    db.session.commit()

    return {
        "message": "Access token refreshed successfully",
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }, 200


# ==========================================
# LOGOUT
# POST /api/auth/logout
# ==========================================

@auth_bp.route("/logout", methods=["POST"])
@jwt_required(refresh=True)
def logout():

    user_id = int(get_jwt_identity())

    raw_token = get_bearer_token()

    if not raw_token:
        return {
            "message": "Refresh token is required"
        }, 401

    token_hash = hash_token(raw_token)

    refresh_record = RefreshToken.query.filter_by(
        user_id=user_id,
        token_hash=token_hash
    ).first()

    if not refresh_record:
        return {
            "message": "Refresh token not recognized"
        }, 401

    refresh_record.revoked = True

    security_event = SecurityEvent(
        user_id=user_id,
        event_type="LOGOUT",
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        details="User logged out and refresh token revoked"
    )

    db.session.add(security_event)

    db.session.commit()

    return {
        "message": "Logout successful"
    }, 200


# ==========================================
# CURRENT USER
# GET /api/auth/me
# ==========================================

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    user = User.query.get(
        int(user_id)
    )

    if not user:
        return {
            "message": "User not found"
        }, 404

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }, 200


# ==========================================
# ADMIN TEST
# GET /api/auth/admin-test
# ==========================================

@auth_bp.route("/admin-test", methods=["GET"])
@role_required("admin")
def admin_test():

    return {
        "message": (
            "Welcome Admin! "
            "You have access to this protected endpoint."
        )
    }, 200