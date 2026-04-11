import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agora.core.config import settings
from agora.core.database import get_db
from agora.core.security import create_access_token, generate_otp
from agora.models.user import OTPCode, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# Le client Twilio n'est initialisé que si les credentials sont configurés
_twilio_client = None
if settings.twilio_enabled:
    from twilio.rest import Client
    _twilio_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)


class SendOTPRequest(BaseModel):
    phone_number: str  # Format international : +33612345678


class VerifyOTPRequest(BaseModel):
    phone_number: str
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool


@router.post("/send-otp", status_code=status.HTTP_200_OK)
def send_otp(payload: SendOTPRequest, db: Session = Depends(get_db)):
    """Envoie un code OTP par SMS au numéro fourni."""
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes)

    # Invalider les anciens OTP non utilisés pour ce numéro
    db.query(OTPCode).filter(
        OTPCode.phone_number == payload.phone_number,
        OTPCode.used == False,
    ).delete()

    otp = OTPCode(
        phone_number=payload.phone_number,
        code=code,
        expires_at=expires_at,
    )
    db.add(otp)
    db.commit()

    if _twilio_client:
        _twilio_client.messages.create(
            body=f"Votre code Agora : {code}. Valable {settings.otp_expire_minutes} minutes.",
            from_=settings.twilio_phone_number,
            to=payload.phone_number,
        )
        return {"message": "Code envoyé par SMS."}
    else:
        # Mode développement : OTP dans les logs, retourné dans la réponse
        logger.warning(f"[DEV] OTP pour {payload.phone_number} : {code}")
        return {"message": "Mode dev — code OTP dans les logs.", "dev_code": code}


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Vérifie le code OTP et retourne un token JWT. Crée le compte si nouveau."""
    otp = (
        db.query(OTPCode)
        .filter(
            OTPCode.phone_number == payload.phone_number,
            OTPCode.code == payload.code,
            OTPCode.used == False,
            OTPCode.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Code invalide ou expiré.",
        )

    otp.used = True

    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    is_new_user = user is None

    if is_new_user:
        user = User(phone_number=payload.phone_number)
        db.add(user)

    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, is_new_user=is_new_user)
