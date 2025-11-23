from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal
import stripe
import razorpay
from app.core.config import settings


class PaymentGateway(ABC):
    """Abstract base class for payment gateways"""

    @abstractmethod
    def create_customer(self, email: str, name: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """Create a customer in the payment gateway"""
        pass

    @abstractmethod
    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payment intent"""
        pass

    @abstractmethod
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm a payment"""
        pass

    @abstractmethod
    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Refund a payment"""
        pass

    @abstractmethod
    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a subscription"""
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        pass


class StripeGateway(PaymentGateway):
    """Stripe payment gateway implementation"""

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_customer(self, email: str, name: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """Create a Stripe customer"""
        customer_data = {
            "email": email,
            "name": name,
        }
        if phone:
            customer_data["phone"] = phone

        customer = stripe.Customer.create(**customer_data)

        return {
            "customer_id": customer.id,
            "email": customer.email,
            "name": customer.name
        }

    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a Stripe payment intent"""
        # Stripe expects amount in cents
        amount_cents = int(amount * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency.lower(),
            customer=customer_id,
            metadata=metadata or {},
            automatic_payment_methods={"enabled": True}
        )

        return {
            "payment_intent_id": intent.id,
            "client_secret": intent.client_secret,
            "status": intent.status,
            "amount": amount
        }

    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm a Stripe payment"""
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        return {
            "payment_id": intent.id,
            "status": intent.status,
            "amount": Decimal(intent.amount) / 100,
            "currency": intent.currency.upper()
        }

    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Refund a Stripe payment"""
        refund_data = {"payment_intent": payment_id}

        if amount:
            refund_data["amount"] = int(amount * 100)

        if reason:
            refund_data["reason"] = reason

        refund = stripe.Refund.create(**refund_data)

        return {
            "refund_id": refund.id,
            "status": refund.status,
            "amount": Decimal(refund.amount) / 100
        }

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a Stripe subscription"""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            metadata=metadata or {},
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"]
        )

        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret
        }

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a Stripe subscription"""
        subscription = stripe.Subscription.delete(subscription_id)

        return {
            "subscription_id": subscription.id,
            "status": subscription.status
        }


class RazorpayGateway(PaymentGateway):
    """Razorpay payment gateway implementation"""

    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_customer(self, email: str, name: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """Create a Razorpay customer"""
        customer_data = {
            "email": email,
            "name": name,
            "fail_existing": "0"
        }
        if phone:
            customer_data["contact"] = phone

        customer = self.client.customer.create(customer_data)

        return {
            "customer_id": customer["id"],
            "email": customer["email"],
            "name": customer["name"]
        }

    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a Razorpay order (equivalent to payment intent)"""
        # Razorpay expects amount in paise (smallest currency unit)
        amount_paise = int(amount * 100)

        order = self.client.order.create({
            "amount": amount_paise,
            "currency": currency,
            "notes": metadata or {}
        })

        return {
            "payment_intent_id": order["id"],
            "client_secret": order["id"],  # Razorpay doesn't have client_secret concept
            "status": order["status"],
            "amount": amount
        }

    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm a Razorpay payment"""
        order = self.client.order.fetch(payment_intent_id)

        return {
            "payment_id": order["id"],
            "status": order["status"],
            "amount": Decimal(order["amount"]) / 100,
            "currency": order["currency"]
        }

    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Refund a Razorpay payment"""
        refund_data = {}

        if amount:
            refund_data["amount"] = int(amount * 100)

        refund = self.client.payment.refund(payment_id, refund_data)

        return {
            "refund_id": refund["id"],
            "status": refund["status"],
            "amount": Decimal(refund["amount"]) / 100
        }

    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a Razorpay subscription"""
        subscription = self.client.subscription.create({
            "plan_id": plan_id,
            "customer_notify": 1,
            "total_count": 12,  # Number of billing cycles
            "notes": metadata or {}
        })

        return {
            "subscription_id": subscription["id"],
            "status": subscription["status"],
            "client_secret": subscription["short_url"]
        }

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a Razorpay subscription"""
        subscription = self.client.subscription.cancel(subscription_id)

        return {
            "subscription_id": subscription["id"],
            "status": subscription["status"]
        }


class PaymentGatewayFactory:
    """Factory to create payment gateway instances"""

    @staticmethod
    def get_gateway(gateway_type: str = "stripe") -> PaymentGateway:
        """Get payment gateway instance"""
        if gateway_type.lower() == "stripe":
            return StripeGateway()
        elif gateway_type.lower() == "razorpay":
            return RazorpayGateway()
        else:
            raise ValueError(f"Unsupported payment gateway: {gateway_type}")
