from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Payment, User
from app.schemas.payments import PaymentCreate, PaymentResponse
from app.utils.auth import get_current_user
from app.utils.logger import setup_logger

# Initialize router and logger
router = APIRouter()
logger = setup_logger("payments")

# ----------------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------------

@router.get("/", response_model=list[PaymentResponse], summary="Get all payments")
def get_all_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve all payments.
    Admins see all; normal users see their own.
    """
    try:
        if current_user.is_admin:
            payments = db.query(Payment).all()
        else:
            payments = db.query(Payment).filter(Payment.user_id == current_user.id).all()

        logger.info(f"Fetched {len(payments)} payments for user {current_user.email}")
        return payments

    except Exception as e:
        logger.error(f"Error fetching payments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED, summary="Create new payment")
def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new payment linked to the current user.
    """
    try:
        new_payment = Payment(
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            status=payment_data.status,
            description=payment_data.description,
            user_id=current_user.id
        )

        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        logger.info(f"Payment {new_payment.id} created by {current_user.email}")
        return new_payment

    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment")


@router.get("/{payment_id}", response_model=PaymentResponse, summary="Get payment by ID")
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a specific payment by ID.
    Normal users can only access their own payments.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if not current_user.is_admin and payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a payment")
def delete_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a payment (admin or owner only).
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if not current_user.is_admin and payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(payment)
    db.commit()

    logger.info(f"Payment {payment_id} deleted by {current_user.email}")
    return {"message": "Payment deleted successfully"}
