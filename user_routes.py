"""
User Routes - Profile, Settings, API Key Management
"""

from flask import Blueprint, request, jsonify, g
from user_model import (
    SessionLocal, get_user_by_id, update_user, get_user_api_keys,
    create_api_key, delete_api_key, get_active_api_key
)
from multi_tenant_middleware import MultiTenantMiddleware
from auth_manager import AuthDecorator

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/profile', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def get_profile():
    """Get current user profile"""
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


@user_bp.route('/profile', methods=['PUT'])
@MultiTenantMiddleware.tenant_required
def update_profile():
    """
    Update user profile

    Request:
    {
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+91-9999999999",
        "company_name": "My Trading Co",
        "timezone": "Asia/Kolkata"
    }
    """
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400

        # Allowed fields to update
        allowed_fields = {
            "first_name", "last_name", "phone", "company_name", "timezone", "bio"
        }

        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        db = SessionLocal()
        user = update_user(db, user_id, **update_data)
        db.close()

        return jsonify({
            "status": "success",
            "message": "Profile updated",
            "data": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


@user_bp.route('/api-keys', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def get_api_keys():
    """Get all API keys for current user"""
    try:
        user_id = g.user_id
        db = SessionLocal()

        # Verify user exists
        user = get_user_by_id(db, user_id)
        if not user:
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        api_keys = get_user_api_keys(db, user_id)
        db.close()

        return jsonify({
            "status": "success",
            "data": [key.to_dict(include_secrets=False) for key in api_keys]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


@user_bp.route('/api-keys', methods=['POST'])
@MultiTenantMiddleware.tenant_required
def add_api_key():
    """
    Add new API key for broker connection

    Request:
    {
        "key_name": "Angel One Main",
        "api_key": "...",
        "api_secret": "...",
        "client_code": "..."
    }
    """
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400

        # Validate required fields
        required = {"key_name", "api_key", "api_secret", "client_code"}
        if not all(field in data for field in required):
            return jsonify({
                "status": "error",
                "message": f"Required fields: {', '.join(required)}"
            }), 400

        key_name = data.get("key_name", "").strip()
        api_key = data.get("api_key", "").strip()
        api_secret = data.get("api_secret", "").strip()
        client_code = data.get("client_code", "").strip()

        # Validate
        if not all([key_name, api_key, api_secret, client_code]):
            return jsonify({
                "status": "error",
                "message": "All fields required and cannot be empty"
            }), 400

        db = SessionLocal()

        # Verify user exists
        user = get_user_by_id(db, user_id)
        if not user:
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        # Create API key
        new_key = create_api_key(
            db, user_id, key_name, api_key, api_secret, client_code
        )
        db.close()

        return jsonify({
            "status": "success",
            "message": "API key added",
            "data": new_key.to_dict(include_secrets=False)
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


@user_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
@MultiTenantMiddleware.tenant_required
def remove_api_key(key_id):
    """Remove API key (owner only)"""
    try:
        user_id = g.user_id
        db = SessionLocal()

        success = delete_api_key(db, key_id, user_id)
        db.close()

        if not success:
            return jsonify({
                "status": "error",
                "message": "API key not found or unauthorized"
            }), 404

        return jsonify({
            "status": "success",
            "message": "API key deleted"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


@user_bp.route('/subscription', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def get_subscription():
    """Get user subscription info"""
    try:
        user_id = g.user_id
        # Mock subscription data
        subscription = {
            'plan': 'free',
            'status': 'active',
            'amount': 0,
            'billing_cycle': 'Monthly',
            'next_renewal': 'N/A'
        }
        return jsonify({
            "status": "success",
            "data": subscription
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route('/billing-history', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def get_billing_history():
    """Get user billing history"""
    try:
        user_id = g.user_id
        # Mock billing history
        history = [
            {'date': '2026-06-15', 'description': 'Pro Plan - Monthly', 'amount': 999, 'status': 'paid'},
            {'date': '2026-05-15', 'description': 'Pro Plan - Monthly', 'amount': 999, 'status': 'paid'},
            {'date': '2026-04-15', 'description': 'Free Plan', 'amount': 0, 'status': 'paid'},
        ]
        return jsonify({
            "status": "success",
            "data": history
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route('/watchlist', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def get_watchlist():
    """Get user watchlist"""
    try:
        user_id = g.user_id
        # Mock watchlist data
        watchlist = [
            {'symbol': 'NIFTY', 'price': 52000, 'change': 100, 'changePercent': 0.19, 'volume': 1000000},
            {'symbol': 'BANKNIFTY', 'price': 48000, 'change': -200, 'changePercent': -0.42, 'volume': 800000},
            {'symbol': 'SENSEX', 'price': 60000, 'change': 300, 'changePercent': 0.50, 'volume': 500000},
        ]
        return jsonify({
            "status": "success",
            "data": watchlist
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route('/watchlist', methods=['POST'])
@MultiTenantMiddleware.tenant_required
def add_watchlist():
    """Add symbol to watchlist"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        return jsonify({
            "status": "success",
            "message": f"{symbol} added to watchlist"
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route('/watchlist/<symbol>', methods=['DELETE'])
@MultiTenantMiddleware.tenant_required
def remove_watchlist(symbol):
    """Remove symbol from watchlist"""
    try:
        return jsonify({
            "status": "success",
            "message": f"{symbol} removed from watchlist"
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@user_bp.route('/preferences', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def get_preferences():
    """Get user preferences"""
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
            "data": {
                "timezone": user.timezone,
                "email_alerts": True,  # Phase 2
                "sms_alerts": False,   # Phase 2
                "daily_summary": True  # Phase 2
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


@user_bp.route('/preferences', methods=['PUT'])
@MultiTenantMiddleware.tenant_required
def update_preferences():
    """Update user preferences"""
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400

        # Phase 2: Store preferences in database
        # For now, just return success

        return jsonify({
            "status": "success",
            "message": "Preferences updated"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


@user_bp.route('/account/deactivate', methods=['POST'])
@MultiTenantMiddleware.tenant_required
def deactivate_account():
    """
    Deactivate user account
    Soft delete - marks as inactive, preserves data
    """
    try:
        user_id = g.user_id
        db = SessionLocal()

        user = update_user(db, user_id, is_active=False)
        db.close()

        return jsonify({
            "status": "success",
            "message": "Account deactivated. You can reactivate by logging in."
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


@user_bp.route('/account/delete', methods=['POST'])
@MultiTenantMiddleware.tenant_required
def delete_account():
    """
    Permanently delete user account and all data
    WARNING: This is irreversible
    """
    try:
        user_id = g.user_id
        data = request.get_json()

        # Require password confirmation
        if not data or "password" not in data:
            return jsonify({
                "status": "error",
                "message": "Password required to delete account"
            }), 400

        # Phase 2: Implement proper deletion with password verification
        return jsonify({
            "status": "info",
            "message": "Account deletion will be enabled in Phase 2 with proper verification"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


@user_bp.route('/activity', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def get_activity():
    """Get user activity log (sessions, logins)"""
    try:
        user_id = g.user_id
        db = SessionLocal()

        # Phase 2: Get session history from user_sessions table
        user = get_user_by_id(db, user_id)
        db.close()

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        return jsonify({
            "status": "success",
            "data": {
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "active_sessions": 1  # Phase 2
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("✅ User routes module ready")
