from fastapi import APIRouter, HTTPException, status, Body
from app.utils.otp import generate_otp, send_otp_email, send_otp_sms

router = APIRouter()

@router.post("/send-otp", status_code=status.HTTP_200_OK)
def send_otp(
    email: str = Body(...),
    phone: str = Body(...)
):
    otp = generate_otp()
    try:
        send_otp_email(email, otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP email: {e}")
    try:
        send_otp_sms(phone, otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP SMS: {e}")
    return {"success": True, "message": "OTP sent via SMS and email.", "otp": otp}  # Remove 'otp' in production
