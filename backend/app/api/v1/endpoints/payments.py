from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe

from app.db.session import get_db
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus, Payout, PayoutStatus
from app.schemas.payment import (
    PaymentIntentCreate, PaymentIntentResponse, PaymentResponse,
    RefundRequest, RefundResponse, PayoutResponse, PayoutSummary,
    ConnectAccountCreate, ConnectAccountResponse
)
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a Stripe payment intent for a booking."""
    # Get booking
    result = await db.execute(select(Booking).where(Booking.id == payment_data.booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is not in pending state"
        )
    
    try:
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.full_name,
                metadata={"user_id": str(current_user.id)}
            )
            current_user.stripe_customer_id = customer.id
            await db.commit()
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=booking.total_amount,
            currency="usd",
            customer=current_user.stripe_customer_id,
            metadata={
                "booking_id": str(booking.id),
                "user_id": str(current_user.id)
            },
            automatic_payment_methods={"enabled": True}
        )
        
        # Store payment intent ID
        booking.payment_intent_id = intent.id
        
        # Create payment record
        payment = Payment(
            booking_id=booking.id,
            user_id=current_user.id,
            stripe_payment_intent_id=intent.id,
            amount=booking.total_amount,
            status=PaymentStatus.PENDING
        )
        db.add(payment)
        
        await db.commit()
        
        return PaymentIntentResponse(
            client_secret=intent.client_secret,
            payment_intent_id=intent.id,
            amount=booking.total_amount,
            currency="usd"
        )
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/confirm-payment")
async def confirm_payment(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirm payment after successful Stripe payment."""
    try:
        # Verify payment intent with Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status != "succeeded":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment has not been completed"
            )
        
        # Update payment record
        result = await db.execute(
            select(Payment).where(Payment.stripe_payment_intent_id == payment_intent_id)
        )
        payment = result.scalar_one_or_none()
        
        if payment:
            payment.status = PaymentStatus.SUCCEEDED
            payment.stripe_charge_id = intent.latest_charge
            
            # Get payment method details
            if intent.payment_method:
                pm = stripe.PaymentMethod.retrieve(intent.payment_method)
                if pm.card:
                    payment.last_four = pm.card.last4
                    payment.card_brand = pm.card.brand
                    payment.payment_method = pm.type
        
        # Update booking status
        booking_result = await db.execute(
            select(Booking).where(Booking.payment_intent_id == payment_intent_id)
        )
        booking = booking_result.scalar_one_or_none()
        
        if booking:
            booking.status = BookingStatus.CONFIRMED
            booking.payment_status = "paid"
        
        await db.commit()
        
        return {"message": "Payment confirmed", "status": "succeeded"}
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        # Update payment and booking status
        result = await db.execute(
            select(Payment).where(Payment.stripe_payment_intent_id == intent["id"])
        )
        payment = result.scalar_one_or_none()
        if payment:
            payment.status = PaymentStatus.SUCCEEDED
            await db.commit()
    
    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        result = await db.execute(
            select(Payment).where(Payment.stripe_payment_intent_id == intent["id"])
        )
        payment = result.scalar_one_or_none()
        if payment:
            payment.status = PaymentStatus.FAILED
            await db.commit()
    
    return {"status": "success"}

@router.post("/refund", response_model=RefundResponse)
async def create_refund(
    refund_data: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a refund for a payment."""
    result = await db.execute(select(Payment).where(Payment.id == refund_data.payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Get booking to verify authorization
    booking_result = await db.execute(select(Booking).where(Booking.id == payment.booking_id))
    booking = booking_result.scalar_one_or_none()
    
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if payment.status != PaymentStatus.SUCCEEDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund successful payments"
        )
    
    try:
        refund_amount = refund_data.amount if refund_data.amount else payment.amount
        
        refund = stripe.Refund.create(
            payment_intent=payment.stripe_payment_intent_id,
            amount=refund_amount,
            reason="requested_by_customer"
        )
        
        from datetime import datetime
        payment.refund_amount = refund_amount
        payment.refund_reason = refund_data.reason
        payment.refunded_at = datetime.utcnow()
        payment.status = PaymentStatus.REFUNDED if refund_amount == payment.amount else PaymentStatus.PARTIALLY_REFUNDED
        
        # Update booking status
        booking.status = BookingStatus.REFUNDED if refund_amount == payment.amount else BookingStatus.CANCELLED
        
        await db.commit()
        await db.refresh(payment)
        
        return RefundResponse(
            id=payment.id,
            original_amount=payment.amount,
            refund_amount=refund_amount,
            status=payment.status,
            refunded_at=payment.refunded_at
        )
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/my-payments", response_model=List[PaymentResponse])
async def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment history for current user."""
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()
    return payments

@router.get("/owner/payouts", response_model=List[PayoutResponse])
async def get_owner_payouts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payout history for parking spot owner."""
    result = await db.execute(
        select(Payout)
        .where(Payout.owner_id == current_user.id)
        .order_by(Payout.created_at.desc())
    )
    payouts = result.scalars().all()
    return payouts

@router.get("/owner/summary", response_model=PayoutSummary)
async def get_payout_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payout summary for parking spot owner."""
    from sqlalchemy import func
    from datetime import datetime
    
    # Total earnings (completed payouts)
    total_result = await db.execute(
        select(func.sum(Payout.amount))
        .where(
            Payout.owner_id == current_user.id,
            Payout.status == PayoutStatus.PAID
        )
    )
    total_earnings = total_result.scalar() or 0
    
    # Pending payouts
    pending_result = await db.execute(
        select(func.sum(Payout.amount))
        .where(
            Payout.owner_id == current_user.id,
            Payout.status == PayoutStatus.PENDING
        )
    )
    pending_payouts = pending_result.scalar() or 0
    
    # Completed payouts count
    completed_result = await db.execute(
        select(func.count(Payout.id))
        .where(
            Payout.owner_id == current_user.id,
            Payout.status == PayoutStatus.PAID
        )
    )
    completed_payouts = completed_result.scalar() or 0
    
    # This month earnings
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_result = await db.execute(
        select(func.sum(Payout.amount))
        .where(
            Payout.owner_id == current_user.id,
            Payout.status == PayoutStatus.PAID,
            Payout.processed_at >= current_month
        )
    )
    this_month_earnings = month_result.scalar() or 0
    
    return PayoutSummary(
        total_earnings=total_earnings,
        pending_payouts=pending_payouts,
        completed_payouts=completed_payouts,
        this_month_earnings=this_month_earnings
    )

@router.post("/connect/create-account", response_model=ConnectAccountResponse)
async def create_connect_account(
    account_data: ConnectAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create Stripe Connect account for owners to receive payouts."""
    try:
        account = stripe.Account.create(
            type="express",
            country=account_data.country,
            email=current_user.email,
            capabilities={
                "transfers": {"requested": True}
            },
            business_type=account_data.business_type,
            metadata={"user_id": str(current_user.id)}
        )
        
        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=f"{settings.BACKEND_CORS_ORIGINS[0]}/owner/onboarding/refresh",
            return_url=f"{settings.BACKEND_CORS_ORIGINS[0]}/owner/onboarding/complete",
            type="account_onboarding"
        )
        
        return ConnectAccountResponse(
            account_id=account.id,
            onboarding_url=account_link.url
        )
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
