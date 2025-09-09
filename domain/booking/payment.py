"""
Payment domain models
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PaymentStatus(Enum):
    """Payment status enumeration"""

    PENDING = "pending"
    PROOF_UPLOADED = "proof_uploaded"
    ADMIN_APPROVED = "admin_approved"
    ADMIN_REJECTED = "admin_rejected"


class PaymentProof(BaseModel):
    """Payment proof model"""

    file_id: str = Field(..., description="Telegram file ID")
    file_type: str = Field(..., description="File type: photo or document")
    file_size: int | None = Field(None, description="File size in bytes")
    uploaded_at: datetime = Field(
        default_factory=datetime.now, description="Upload timestamp"
    )
    user_id: int = Field(..., description="User ID who uploaded the proof")

    class Config:
        from_attributes = True


class PaymentInfo(BaseModel):
    """Payment information model"""

    card_number: str = Field(..., description="Payment card number")
    phone_number: str = Field(..., description="Payment phone number")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="BYN", description="Payment currency")

    class Config:
        from_attributes = True
