"""
Billing Routes - Subscription management and Stripe integration
Phase 2: Payment processing and subscription lifecycle
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta
from subscription_model import (
    SessionLocal, get_user_subscription, create_subscription, upgrade_subscription,
    get_user_usage, get_user_invoices, SUBSCRIPTION_TIERS, init_subscription_db
)
from user_model import get_user_by_id
from multi_tenant_middleware import MultiTenantMiddleware
from auth_manager import AuthDecorator
from email_service import NotificationSender
import os
import json

billing_bp = Blueprint('billing', __name__, url_prefix='/api/billing')

# Initialize subscription database on import
init_subscription_db()


# ===== SUBSCRIPTION ENDPOINTS =====
@billing_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get available subscription plans"""
    plans = []
    for tier, details in SUBSCRIPTION_TIERS.items():
        plans.append({
            "tier": tier,
            "name": details["name"],
            "monthly_price": details["price"],
            "annual_price": details["price"] * 10,
            "signals_limit": details["signals_per_month"],
            "api_calls_limit": details["api_calls_per_day"],
            "brokers_supported": details["brokers_supported"],
            "features": details["features"],
            "priority_support": details["priority_support"]
        })

    return jsonify({
        "status": "success",
        "data": plans
    }), 200


@billing_bp.route('/subscription', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def get_subscription():
    """Get current user subscription"""
    try:
        user_id = g.user_id
        db = SessionLocal()

        subscription = get_user_subscription(db, user_id)
        db.close()

        if not subscription:
            return jsonify({
                "status": "error",
                "message": "No subscription found"
            }), 404

        return jsonify({
            "status": "success",
            "data": {
                **subscription.to_dict(),
                "is_active": subscription.is_active(),
                "days_remaining": subscription.days_remaining()
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@billing_bp.route('/upgrade', methods=['POST'])
@MultiTenantMiddleware.tenant_required
def upgrade_plan():
    """
    Upgrade subscription plan

    Request:
    {
        "plan_tier": "pro",
        "billing_cycle": "monthly"
    }
    """
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data or "plan_tier" not in data:
            return jsonify({
                "status": "error",
                "message": "Plan tier required"
            }), 400

        plan_tier = data.get("plan_tier").lower()

        if plan_tier not in SUBSCRIPTION_TIERS:
            return jsonify({
                "status": "error",
                "message": f"Invalid plan tier. Available: {list(SUBSCRIPTION_TIERS.keys())}"
            }), 400

        db = SessionLocal()
        user = get_user_by_id(db, user_id)

        if not user:
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        # Upgrade subscription
        subscription = upgrade_subscription(db, user_id, plan_tier)
        db.close()

        # Send confirmation email
        plan_info = SUBSCRIPTION_TIERS[plan_tier]
        next_billing = (datetime.utcnow() + timedelta(days=30)).strftime("%B %d, %Y")
        NotificationSender.send_subscription_confirmation(
            user.email,
            user.first_name,
            plan_tier,
            plan_info["price"],
            next_billing
        )

        return jsonify({
            "status": "success",
            "message": f"Upgraded to {plan_tier.title()} plan",
            "data": subscription.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@billing_bp.route('/downgrade', methods=['POST'])
@MultiTenantMiddleware.tenant_required
def downgrade_plan():
    """Downgrade subscription plan"""
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data or "plan_tier" not in data:
            return jsonify({
                "status": "error",
                "message": "Plan tier required"
            }), 400

        plan_tier = data.get("plan_tier").lower()

        db = SessionLocal()
        subscription = upgrade_subscription(db, user_id, plan_tier)
        db.close()

        return jsonify({
            "status": "success",
            "message": f"Downgraded to {plan_tier.title()} plan",
            "data": subscription.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@billing_bp.route('/cancel', methods=['POST'])
@MultiTenantMiddleware.tenant_required
def cancel_subscription():
    """Cancel subscription"""
    try:
        user_id = g.user_id
        db = SessionLocal()

        subscription = get_user_subscription(db, user_id)
        if not subscription:
            db.close()
            return jsonify({
                "status": "error",
                "message": "No subscription found"
            }), 404

        subscription.status = "canceled"
        subscription.canceled_at = datetime.utcnow()
        subscription.auto_renew = False
        db.commit()

        user = get_user_by_id(db, user_id)
        db.close()

        return jsonify({
            "status": "success",
            "message": "Subscription canceled"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ===== USAGE TRACKING =====
@billing_bp.route('/usage', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def get_usage():
    """Get current month usage"""
    try:
        user_id = g.user_id
        db = SessionLocal()

        subscription = get_user_subscription(db, user_id)
        if not subscription:
            db.close()
            return jsonify({
                "status": "error",
                "message": "No subscription found"
            }), 404

        usage = get_user_usage(db, user_id)
        plan = SUBSCRIPTION_TIERS.get(subscription.plan.tier if subscription.plan else "free")

        db.close()

        return jsonify({
            "status": "success",
            "data": {
                "current_plan": subscription.plan.tier if subscription.plan else "free",
                "signals_generated": usage.signals_generated if usage else 0,
                "signals_limit": plan["signals_per_month"],
                "api_calls": usage.api_calls if usage else 0,
                "api_calls_limit": plan["api_calls_per_day"] * 30,
                "brokers_connected": usage.brokers_connected if usage else 0,
                "brokers_supported": plan["brokers_supported"],
                "usage_percentage": {
                    "signals": int((usage.signals_generated if usage else 0) / plan["signals_per_month"] * 100),
                    "api_calls": int((usage.api_calls if usage else 0) / (plan["api_calls_per_day"] * 30) * 100)
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ===== INVOICES =====
@billing_bp.route('/invoices', methods=['GET'])
@MultiTenantMiddleware.tenant_required
def list_invoices():
    """Get user invoices"""
    try:
        user_id = g.user_id
        limit = request.args.get('limit', 20, type=int)

        db = SessionLocal()
        invoices = get_user_invoices(db, user_id, limit)
        db.close()

        return jsonify({
            "status": "success",
            "data": [inv.to_dict() for inv in invoices]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ===== STRIPE WEBHOOKS =====
@billing_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')

        # Verify webhook signature
        stripe_key = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not stripe_key:
            return jsonify({"status": "error", "message": "Webhook secret not configured"}), 400

        try:
            import stripe
            stripe.api_key = os.getenv("STRIPE_API_KEY")
            event = stripe.Webhook.construct_event(payload, sig_header, stripe_key)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

        # Handle different event types
        if event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])

        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_canceled(event['data']['object'])

        elif event['type'] == 'invoice.payment_succeeded':
            handle_payment_succeeded(event['data']['object'])

        elif event['type'] == 'invoice.payment_failed':
            handle_payment_failed(event['data']['object'])

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def handle_subscription_updated(subscription):
    """Handle subscription update"""
    db = SessionLocal()
    # Update subscription in database based on stripe_subscription_id
    db.close()


def handle_subscription_canceled(subscription):
    """Handle subscription cancellation"""
    db = SessionLocal()
    # Mark subscription as canceled
    db.close()


def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    db = SessionLocal()
    # Update invoice status to paid
    db.close()


def handle_payment_failed(invoice):
    """Handle failed payment"""
    db = SessionLocal()
    # Update invoice status and send notification
    db.close()


# ===== PAYMENT ROUTES =====
@billing_bp.route('/create-payment-intent', methods=['POST'])
@MultiTenantMiddleware.tenant_required
def create_payment_intent():
    """Create Stripe payment intent"""
    try:
        user_id = g.user_id
        data = request.get_json()

        amount = data.get("amount", 0)
        if amount <= 0:
            return jsonify({
                "status": "error",
                "message": "Invalid amount"
            }), 400

        # Create Stripe payment intent
        try:
            import stripe
            stripe.api_key = os.getenv("STRIPE_API_KEY")

            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency="inr",
                metadata={"user_id": user_id}
            )

            return jsonify({
                "status": "success",
                "data": {
                    "client_secret": intent.client_secret,
                    "payment_intent_id": intent.id
                }
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Payment processing error: {str(e)}"
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    print("✅ Billing routes module ready")
