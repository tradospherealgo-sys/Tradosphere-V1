"""
Admin Routes - User management, analytics, and admin controls
Phase 2: Admin panel with user management and system analytics
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta
from user_model import SessionLocal, get_user_by_id, update_user
from subscription_model import (
    SessionLocal as SubSessionLocal, get_user_subscription,
    UsageMetrics, Invoice
)
from multi_tenant_middleware import MultiTenantMiddleware
from auth_manager import AuthDecorator
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def is_admin(f):
    """Decorator to check if user is admin"""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = g.user_id
        db = SessionLocal()
        user = get_user_by_id(db, user_id)
        db.close()

        if not user or not user.is_admin:
            return jsonify({
                "status": "error",
                "message": "Admin access required"
            }), 403

        return f(*args, **kwargs)

    return decorated


# ===== USER MANAGEMENT =====
@admin_bp.route('/users', methods=['GET'])
@MultiTenantMiddleware.tenant_required
@is_admin
def list_users():
    """List all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        search = request.args.get('search', '')

        db = SessionLocal()
        from user_model import User

        query = db.query(User)

        if search:
            query = query.filter(
                (User.email.ilike(f"%{search}%")) |
                (User.first_name.ilike(f"%{search}%")) |
                (User.last_name.ilike(f"%{search}%"))
            )

        total = query.count()
        users = query.offset((page - 1) * limit).limit(limit).all()
        db.close()

        return jsonify({
            "status": "success",
            "data": [u.to_dict() for u in users],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@MultiTenantMiddleware.tenant_required
@is_admin
def get_user_details(user_id):
    """Get detailed user information"""
    try:
        db = SessionLocal()
        user = get_user_by_id(db, user_id)

        if not user:
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        subscription = get_user_subscription(db, user_id)
        db.close()

        return jsonify({
            "status": "success",
            "data": {
                **user.to_dict(),
                "subscription": subscription.to_dict() if subscription else None,
                "is_admin": user.is_admin,
                "is_verified": user.is_verified,
                "is_active": user.is_active
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>/promote', methods=['POST'])
@MultiTenantMiddleware.tenant_required
@is_admin
def promote_to_admin(user_id):
    """Promote user to admin"""
    try:
        db = SessionLocal()
        user = get_user_by_id(db, user_id)

        if not user:
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        user = update_user(db, user_id, is_admin=True)
        db.close()

        return jsonify({
            "status": "success",
            "message": f"User {user.email} promoted to admin",
            "data": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>/disable', methods=['POST'])
@MultiTenantMiddleware.tenant_required
@is_admin
def disable_user(user_id):
    """Disable user account"""
    try:
        db = SessionLocal()
        user = get_user_by_id(db, user_id)

        if not user:
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        user = update_user(db, user_id, is_active=False)
        db.close()

        return jsonify({
            "status": "success",
            "message": f"User {user.email} disabled"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>/enable', methods=['POST'])
@MultiTenantMiddleware.tenant_required
@is_admin
def enable_user(user_id):
    """Enable user account"""
    try:
        db = SessionLocal()
        user = update_user(db, user_id, is_active=True)
        db.close()

        return jsonify({
            "status": "success",
            "message": f"User {user.email} enabled"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ===== ANALYTICS =====
@admin_bp.route('/analytics/overview', methods=['GET'])
@MultiTenantMiddleware.tenant_required
@is_admin
def analytics_overview():
    """Get platform analytics overview"""
    try:
        db = SessionLocal()
        from user_model import User

        # User statistics
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        new_users_today = db.query(func.count(User.id)).filter(
            User.created_at >= datetime.utcnow() - timedelta(days=1)
        ).scalar()

        # Subscription statistics
        from subscription_model import UserSubscription, SubscriptionPlan
        sub_db = SubSessionLocal()

        active_subscriptions = sub_db.query(func.count(UserSubscription.id)).filter(
            UserSubscription.status == "active"
        ).scalar()

        pro_users = sub_db.query(func.count(UserSubscription.id)).join(
            SubscriptionPlan
        ).filter(SubscriptionPlan.tier == "pro").scalar()

        enterprise_users = sub_db.query(func.count(UserSubscription.id)).join(
            SubscriptionPlan
        ).filter(SubscriptionPlan.tier == "enterprise").scalar()

        # Revenue
        total_revenue = sub_db.query(func.sum(Invoice.amount)).filter(
            Invoice.status == "paid"
        ).scalar()

        sub_db.close()
        db.close()

        return jsonify({
            "status": "success",
            "data": {
                "users": {
                    "total": total_users or 0,
                    "active": active_users or 0,
                    "new_today": new_users_today or 0
                },
                "subscriptions": {
                    "active": active_subscriptions or 0,
                    "pro": pro_users or 0,
                    "enterprise": enterprise_users or 0
                },
                "revenue": {
                    "total": float(total_revenue) if total_revenue else 0.0,
                    "currency": "INR",
                    "period": "all_time"
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route('/analytics/usage', methods=['GET'])
@MultiTenantMiddleware.tenant_required
@is_admin
def analytics_usage():
    """Get platform usage analytics"""
    try:
        db = SubSessionLocal()

        # Get current month usage
        current_month = datetime.utcnow().strftime("%Y-%m")
        total_signals = db.query(func.sum(UsageMetrics.signals_generated)).filter(
            UsageMetrics.month == current_month
        ).scalar()

        total_api_calls = db.query(func.sum(UsageMetrics.api_calls)).filter(
            UsageMetrics.month == current_month
        ).scalar()

        total_pnl = db.query(func.sum(UsageMetrics.total_pnl)).filter(
            UsageMetrics.month == current_month
        ).scalar()

        db.close()

        return jsonify({
            "status": "success",
            "data": {
                "period": current_month,
                "metrics": {
                    "total_signals": total_signals or 0,
                    "total_api_calls": total_api_calls or 0,
                    "total_pnl": float(total_pnl) if total_pnl else 0.0,
                    "avg_pnl_per_user": float((total_pnl or 0) / max(1, (db.query(func.count(UsageMetrics.user_id)).filter(UsageMetrics.month == current_month).scalar() or 1)))
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ===== SYSTEM HEALTH =====
@admin_bp.route('/health', methods=['GET'])
@MultiTenantMiddleware.tenant_required
@is_admin
def system_health():
    """Get system health status"""
    try:
        db = SessionLocal()

        # Test database connection
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except:
            db_status = "unhealthy"

        db.close()

        return jsonify({
            "status": "success",
            "data": {
                "timestamp": datetime.utcnow().isoformat(),
                "database": db_status,
                "api": "healthy",
                "overall": "healthy" if db_status == "healthy" else "degraded"
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ===== SYSTEM CONFIGURATION =====
@admin_bp.route('/config', methods=['GET'])
@MultiTenantMiddleware.tenant_required
@is_admin
def get_config():
    """Get system configuration (non-sensitive)"""
    try:
        import os

        return jsonify({
            "status": "success",
            "data": {
                "environment": os.getenv("ENVIRONMENT", "development"),
                "version": "3.0 Phase 2",
                "broker": "Angel One",
                "features": {
                    "multi_tenant": True,
                    "subscriptions": True,
                    "email_notifications": True,
                    "multi_broker": "coming_soon"
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ===== AUDIT LOG =====
@admin_bp.route('/audit-log', methods=['GET'])
@MultiTenantMiddleware.tenant_required
@is_admin
def get_audit_log():
    """Get system audit log"""
    try:
        # Phase 2: Implement comprehensive audit logging
        return jsonify({
            "status": "success",
            "message": "Audit logging will be implemented in Phase 2.5",
            "data": []
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    print("✅ Admin routes module ready")
