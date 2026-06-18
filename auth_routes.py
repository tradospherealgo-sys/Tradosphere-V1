"""
Authentication Routes - Signup, Login, Logout, Token Refresh
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime
from user_model import (
    SessionLocal, get_user_by_email, create_user, get_user_by_id,
    create_session, get_user_sessions
)
from auth_manager import (
    PasswordManager, JWTManager, EmailValidator, AuthDecorator
)
from leads_model import SessionLocal as LeadsSessionLocal, create_lead, convert_lead_to_customer, get_lead_by_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    User signup endpoint

    Request:
    {
        "email": "user@example.com",
        "password": "SecurePassword123",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        email = data.get("email", "").strip()
        password = data.get("password", "")
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()

        # Validation
        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password required"
            }), 400

        if not EmailValidator.is_valid_email(email):
            return jsonify({
                "status": "error",
                "message": "Invalid email format"
            }), 400

        if len(password) < 6:
            return jsonify({
                "status": "error",
                "message": "Password must be at least 6 characters"
            }), 400

        # Normalize email
        email = EmailValidator.normalize_email(email)

        # Check if user exists
        db = SessionLocal()
        existing_user = get_user_by_email(db, email)
        if existing_user:
            db.close()
            return jsonify({
                "status": "error",
                "message": "Email already registered"
            }), 409

        # Hash password
        try:
            password_hash = PasswordManager.hash_password(password)
        except ValueError as e:
            db.close()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400

        # Create user
        user = create_user(db, email, password_hash, first_name, last_name)
        user_id = user.id
        user_email = user.email
        user_dict = user.to_dict()

        # Generate tokens
        tokens = JWTManager.generate_tokens(user_id, user_email)

        # Create session
        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")
        create_session(db, user_id, tokens["access_token"], ip_address, user_agent)

        db.close()

        # Convert lead to customer
        try:
            leads_db = LeadsSessionLocal()
            convert_lead_to_customer(leads_db, email, user_id, "free")
            leads_db.close()
        except Exception as lead_error:
            print(f"⚠️  Lead conversion failed: {lead_error}")

        return jsonify({
            "status": "success",
            "message": "Signup successful",
            "data": {
                "user": user_dict,
                "tokens": tokens
            }
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Signup error: {str(e)}"
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint

    Request:
    {
        "email": "user@example.com",
        "password": "SecurePassword123"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password required"
            }), 400

        # Normalize email
        email = EmailValidator.normalize_email(email)

        db = SessionLocal()

        # Find user
        user = get_user_by_email(db, email)
        if not user:
            db.close()
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        # Check if active
        if not user.is_active:
            db.close()
            return jsonify({
                "status": "error",
                "message": "Account is disabled"
            }), 403

        # Verify password
        if not PasswordManager.verify_password(password, user.password_hash):
            db.close()
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        # Generate tokens
        user_id = user.id
        user_email = user.email
        user_dict = user.to_dict()
        tokens = JWTManager.generate_tokens(user_id, user_email)

        # Update last login
        user.last_login = datetime.utcnow()

        # Create session
        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")
        create_session(db, user_id, tokens["access_token"], ip_address, user_agent)

        db.commit()
        db.close()

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "data": {
                "user": user_dict,
                "tokens": tokens
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Login error: {str(e)}"
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@AuthDecorator.token_required
def logout():
    """
    Logout endpoint - invalidate current session
    """
    try:
        user_id = g.user_id

        db = SessionLocal()

        # Get current sessions and mark as inactive
        sessions = get_user_sessions(db, user_id)
        for session in sessions:
            session.is_active = False

        db.commit()
        db.close()

        return jsonify({
            "status": "success",
            "message": "Logout successful"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Logout error: {str(e)}"
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token using refresh token

    Request:
    {
        "refresh_token": "..."
    }
    """
    try:
        data = request.get_json()

        if not data or "refresh_token" not in data:
            return jsonify({
                "status": "error",
                "message": "Refresh token required"
            }), 400

        refresh_token = data.get("refresh_token")

        # Verify refresh token
        payload = JWTManager.verify_token(refresh_token, token_type="refresh")
        if not payload:
            return jsonify({
                "status": "error",
                "message": "Invalid or expired refresh token"
            }), 401

        # Generate new access token
        new_access_token = JWTManager.refresh_access_token(refresh_token)
        if not new_access_token:
            return jsonify({
                "status": "error",
                "message": "Failed to generate new token"
            }), 500

        return jsonify({
            "status": "success",
            "message": "Token refreshed",
            "data": {
                "access_token": new_access_token,
                "token_type": "Bearer",
                "expires_in": 24 * 3600
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Token refresh error: {str(e)}"
        }), 500


@auth_bp.route('/me', methods=['GET'])
@AuthDecorator.token_required
def get_current_user():
    """
    Get current logged-in user info
    """
    try:
        user_id = g.user_id

        db = SessionLocal()
        user = get_user_by_id(db, user_id)
        db.close()

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        return jsonify({
            "status": "success",
            "data": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """
    Verify email address (Phase 2 feature - email sending)
    """
    return jsonify({
        "status": "info",
        "message": "Email verification coming in Phase 2"
    }), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset (Phase 2 feature - email sending)
    """
    return jsonify({
        "status": "info",
        "message": "Password reset coming in Phase 2"
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
@AuthDecorator.token_required
def reset_password():
    """
    Reset password (authenticated user)

    Request:
    {
        "old_password": "CurrentPassword",
        "new_password": "NewPassword123"
    }
    """
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        old_password = data.get("old_password", "")
        new_password = data.get("new_password", "")

        if not old_password or not new_password:
            return jsonify({
                "status": "error",
                "message": "Old and new passwords required"
            }), 400

        if len(new_password) < 6:
            return jsonify({
                "status": "error",
                "message": "New password must be at least 6 characters"
            }), 400

        db = SessionLocal()
        user = get_user_by_id(db, user_id)

        if not user:
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        # Verify old password
        if not PasswordManager.verify_password(old_password, user.password_hash):
            db.close()
            return jsonify({
                "status": "error",
                "message": "Old password is incorrect"
            }), 401

        # Hash and update new password
        user.password_hash = PasswordManager.hash_password(new_password)
        db.commit()
        db.close()

        return jsonify({
            "status": "success",
            "message": "Password reset successful"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Password reset error: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("✅ Auth routes module ready")
