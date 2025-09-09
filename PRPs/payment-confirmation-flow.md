# Booking Payment Confirmation Flow

## Goal
Implement a payment confirmation system that transitions booking from user confirmation to payment collection and admin approval workflow. When user confirms booking details, show payment options, accept document/photo proof of payment, and notify admin with approval buttons.

## Why
- **Business value**: Converts confirmed bookings into actual revenue by handling payment collection
- **Integration**: Extends existing booking graph completion flow with payment verification
- **Problem solved**: Bridges gap between booking confirmation and final booking approval via admin oversight

## What
User-visible behavior:
1. After booking confirmation, show payment message with card/phone details
2. Accept screenshot/PDF as payment proof 
3. Send notification to admin chat with booking details and action buttons
4. Admin can confirm, cancel, change cost, or change final price

Technical requirements:
- Extend existing booking graph finalization flow
- Handle document/photo uploads in Telegram
- Admin notification service with inline keyboards
- Mock payment details configuration
- Admin chat ID configuration

### Success Criteria
- [ ] Payment message displays with mock card/phone details
- [ ] Document/photo uploads are processed and stored
- [ ] Admin receives booking notification with inline keyboard buttons
- [ ] Admin buttons trigger callback handlers for approval actions
- [ ] Payment confirmation integrates seamlessly with existing booking flow
- [ ] All tests pass for new payment confirmation components

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window

- file: infrastructure/llm/graphs/booking/booking_graph.py
  why: Current finalize() function needs extension for payment flow. Contains booking state management patterns to follow.
  
- file: apps/telegram_bot/handlers/messages.py
  why: Message handling patterns for document/photo processing. Shows existing Telegram interaction patterns.

- file: apps/telegram_bot/handlers/callbacks.py  
  why: Callback handling patterns for admin button interactions. Shows existing callback processing.

- file: core/config.py
  why: Configuration patterns for adding payment card numbers and admin chat ID settings.

- url: https://core.telegram.org/bots/api#inlinekeyboardmarkup
  section: InlineKeyboardMarkup and InlineKeyboardButton
  critical: Required for admin notification buttons implementation

- url: https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/magic_filters.html
  why: Aiogram 3.x filter patterns for document/photo message filtering

- file: domain/booking/ports.py  
  why: NotificationService pattern to extend for admin notifications
  
- file: infrastructure/llm/graphs/common/graph_state.py
  why: State management patterns for extending BookingState with payment fields
```

### Current Codebase Tree
```bash
secret-house-booking-bot-llm/
├── apps/telegram_bot/
│   ├── handlers/
│   │   ├── messages.py          # Message handlers (extend for doc/photo)
│   │   └── callbacks.py         # Callback handlers (extend for admin buttons)
│   └── main.py
├── core/
│   └── config.py               # Settings (add payment config here)
├── domain/booking/
│   ├── entities.py             # Booking models
│   └── ports.py                # Notification service port
├── infrastructure/llm/graphs/
│   ├── booking/
│   │   └── booking_graph.py    # Main booking flow (extend finalize())
│   └── common/
│       └── graph_state.py      # State models (extend BookingState)
└── application/services/
    └── booking_service.py      # Business logic
```

### Desired Codebase Tree with New Files
```bash
secret-house-booking-bot-llm/
├── apps/telegram_bot/
│   └── handlers/
│       └── payments.py         # NEW: Payment document handlers
├── core/
│   └── config.py              # MODIFY: Add payment config
├── domain/booking/
│   ├── entities.py            # MODIFY: Add payment status to Booking
│   └── payment.py             # NEW: Payment domain models  
├── infrastructure/
│   ├── notifications/
│   │   └── admin_service.py   # NEW: Admin notification service
│   └── llm/graphs/booking/
│       └── booking_graph.py   # MODIFY: Extend finalize() with payment
└── tests/
    ├── unit/apps/telegram_bot/handlers/
    │   └── test_payments.py    # NEW: Payment handler tests
    └── integration/
        └── test_payment_flow.py # NEW: End-to-end payment flow tests
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Aiogram 3.x requires specific filters for document/photo
from aiogram.filters import Document, Photo
from aiogram.types import Document as DocumentType, PhotoSize

# GOTCHA: Telegram file downloads have size limits
# Files >20MB require different handling (use file_id, not direct download)

# CRITICAL: Inline keyboards require specific callback_data format
# Max 64 bytes per callback_data, use JSON encoding for complex data

# PATTERN: This project uses async/await throughout
# All new handlers must be async functions

# GOTCHA: Redis state storage requires serializable objects
# Use Pydantic models for complex state, not plain dicts

# CRITICAL: LangGraph state updates must return complete state updates
# Don't mutate existing state, return new state dict
```

## Implementation Blueprint

### Data Models and Structure

Create payment domain models for type safety and state management:
```python
# domain/booking/payment.py
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentStatus(Enum):
    PENDING = "pending"
    PROOF_UPLOADED = "proof_uploaded" 
    ADMIN_APPROVED = "admin_approved"
    ADMIN_REJECTED = "admin_rejected"

class PaymentProof(BaseModel):
    file_id: str
    file_type: str  # "photo" or "document"
    file_size: Optional[int]
    uploaded_at: datetime
    user_id: int

class PaymentInfo(BaseModel):
    card_number: str
    phone_number: str
    amount: float
    currency: str = "BYN"
```

### Task List (Implementation Order)

```yaml
Task 1 - Extend Configuration:
MODIFY core/config.py:
  - ADD payment card number mock setting
  - ADD admin chat ID setting  
  - FOLLOW existing Field() patterns with env vars
  
Task 2 - Extend Domain Models:
MODIFY domain/booking/entities.py:
  - ADD payment_status: PaymentStatus field to Booking
  - ADD payment_proof: Optional[PaymentProof] field
  
CREATE domain/booking/payment.py:
  - IMPLEMENT PaymentStatus, PaymentProof, PaymentInfo models
  - USE Pydantic v2 patterns from existing entities
  
Task 3 - Extend Booking Graph State:
MODIFY infrastructure/llm/graphs/common/graph_state.py:
  - ADD payment_status, payment_proof fields to BookingState
  - MAINTAIN TypedDict pattern consistency
  
Task 4 - Create Admin Notification Service:
CREATE infrastructure/notifications/admin_service.py:
  - IMPLEMENT AdminNotificationService class
  - MIRROR pattern from existing services in application/services/
  - USE aiogram Bot instance for sending messages
  - IMPLEMENT inline keyboard generation for admin actions
  
Task 5 - Extend Booking Graph Payment Flow:
MODIFY infrastructure/llm/graphs/booking/booking_graph.py:
  - REPLACE finalize() mock implementation 
  - ADD payment_request() node before finalize()
  - ADD await_payment_proof() conditional routing
  - MAINTAIN existing branch() logic patterns
  
Task 6 - Create Payment Handlers:
CREATE apps/telegram_bot/handlers/payments.py:
  - IMPLEMENT document/photo handlers with Document/Photo filters
  - ADD file download and storage logic
  - TRIGGER admin notification on upload
  - FOLLOW existing handler patterns in messages.py
  
Task 7 - Create Admin Callback Handlers:
MODIFY apps/telegram_bot/handlers/callbacks.py:
  - ADD admin action handlers (confirm/cancel/change_cost/change_price)
  - PARSE callback_data for booking_id and action
  - UPDATE booking status and notify user
  - FOLLOW existing callback handler patterns
  
Task 8 - Integrate Payment Handlers:
MODIFY apps/telegram_bot/main.py:
  - IMPORT payment handlers router
  - REGISTER payment router with dispatcher
  - MAINTAIN existing router registration patterns
```

### Per Task Pseudocode

```python
# Task 1: Configuration Extension
class Settings(BaseSettings):
    # Existing settings...
    
    # NEW: Payment Configuration
    payment_card_number: str = Field("1234 5678 9012 3456", env="PAYMENT_CARD_NUMBER") 
    payment_phone_number: str = Field("+375291234567", env="PAYMENT_PHONE_NUMBER")
    admin_chat_id: int = Field(-1001234567890, env="ADMIN_CHAT_ID")

# Task 4: Admin Service Pattern  
class AdminNotificationService:
    def __init__(self, bot: Bot, admin_chat_id: int):
        self.bot = bot
        self.admin_chat_id = admin_chat_id
    
    async def notify_new_booking(self, booking: Booking, payment_proof: PaymentProof):
        # PATTERN: Use InlineKeyboardMarkup from aiogram
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve:{booking.id}")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel:{booking.id}")],
            [InlineKeyboardButton(text="💰 Изменить стоимость", callback_data=f"change_cost:{booking.id}")],
            [InlineKeyboardButton(text="💵 Изменить итог", callback_data=f"change_final:{booking.id}")]
        ])
        
        # CRITICAL: Build admin message with all booking details
        message = self._build_booking_summary(booking)
        await self.bot.send_message(self.admin_chat_id, message, reply_markup=keyboard)

# Task 5: Booking Graph Extension
async def payment_request(state: BookingState) -> BookingState:
    """Show payment details and request proof"""
    payment_message = f"""
💳 Оплата бронирования

Переведите сумму на карту: {settings.payment_card_number}
Или на телефон: {settings.payment_phone_number}

Сумма: {state['context'].get('total_cost', 'Рассчитывается')} BYN

📸 Пришлите скриншот или документ об оплате
    """
    
    return {
        "reply": payment_message,
        "payment_status": PaymentStatus.PENDING.value,
        "await_input": True,
        "active_subgraph": "booking"
    }

# Task 6: Payment Handlers Pattern
@router.message(Document())
async def handle_payment_document(message: Message, state: FSMContext):
    """Handle document upload as payment proof"""
    # PATTERN: Download file and store proof
    file_info = await bot.get_file(message.document.file_id)
    
    payment_proof = PaymentProof(
        file_id=message.document.file_id,
        file_type="document", 
        file_size=message.document.file_size,
        uploaded_at=datetime.now(),
        user_id=message.from_user.id
    )
    
    # CRITICAL: Update graph state and notify admin
    await update_booking_state(message.from_user.id, {"payment_proof": payment_proof})
    await admin_service.notify_new_booking(booking, payment_proof)

# Task 7: Admin Callback Pattern
@router.callback_query(lambda c: c.data.startswith("approve:"))
async def handle_admin_approval(callback: CallbackQuery):
    """Handle admin booking approval"""
    booking_id = callback.data.split(":")[1]
    
    # PATTERN: Update booking status and notify user
    await booking_service.approve_booking(booking_id)
    await bot.send_message(user_chat_id, "✅ Ваше бронирование подтверждено!")
    
    # PATTERN: Edit admin message to show action taken
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ ПОДТВЕРЖДЕНО админом",
        reply_markup=None
    )
```

### Integration Points
```yaml
GRAPH_FLOW:
  - current: ask_or_fill -> finalize 
  - new: ask_or_fill -> payment_request -> await_payment -> finalize
  
STATE_MANAGEMENT:
  - extend: BookingState with payment fields
  - storage: Redis with existing FSM integration
  
NOTIFICATIONS:
  - extend: NotificationService port with admin methods
  - implementation: AdminNotificationService with inline keyboards
  
FILE_HANDLING:
  - pattern: Use aiogram file download utilities
  - storage: Store file_id and metadata only (not file contents)
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
uv run ruff check infrastructure/notifications/ apps/telegram_bot/handlers/payments.py domain/booking/payment.py --fix
uv run ruff format infrastructure/notifications/ apps/telegram_bot/handlers/payments.py domain/booking/payment.py
uv run mypy infrastructure/notifications/ apps/telegram_bot/handlers/payments.py domain/booking/payment.py

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```python
# CREATE test_payment_flow.py with these test cases:
def test_payment_request_node():
    """Payment request shows correct card details"""
    state = BookingState(context={"total_cost": 150})
    result = await payment_request(state)
    assert "1234 5678 9012 3456" in result["reply"]
    assert result["payment_status"] == "pending"

def test_admin_notification_keyboard():
    """Admin notification has correct inline keyboard"""
    keyboard = admin_service._build_admin_keyboard(booking_id="123")
    assert len(keyboard.inline_keyboard) == 4  # 4 buttons
    assert "approve:123" in str(keyboard)

def test_document_handler_creates_proof():
    """Document upload creates PaymentProof"""
    # Mock document message
    result = await handle_payment_document(mock_document_message, mock_state)
    assert result["payment_proof"]["file_type"] == "document"

def test_admin_approval_callback():
    """Admin approval updates booking status"""
    callback_data = "approve:123"
    await handle_admin_approval(mock_callback(callback_data))
    # Verify booking status updated and user notified
```

```bash
# Run and iterate until passing:
uv run pytest tests/unit/apps/telegram_bot/handlers/test_payments.py -v
uv run pytest tests/integration/test_payment_flow.py -v  
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Test the complete flow manually:
# 1. Complete booking through existing flow
# 2. Confirm booking - should show payment message
# 3. Send document/photo - admin should receive notification
# 4. Click admin button - should update booking and notify user

# Test with bot:
PYTHONPATH=/Users/a/secret-house-booking-bot-llm python apps/telegram_bot/main.py

# Expected: Complete payment flow works end-to-end
# If error: Check logs for LangGraph state transitions and message handling
```

## Final Validation Checklist
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check .`
- [ ] No type errors: `uv run mypy .`
- [ ] Manual flow test successful: Complete booking -> payment -> admin approval
- [ ] Admin receives notification with working buttons
- [ ] Payment proof is properly stored and displayed
- [ ] User receives confirmation after admin approval
- [ ] Configuration properly loaded from environment variables

---

## Anti-Patterns to Avoid
- ❌ Don't store actual payment card numbers in code - use mock/config only
- ❌ Don't download large files to memory - use file_id for reference
- ❌ Don't hardcode admin chat ID - use configuration
- ❌ Don't mutate LangGraph state directly - return new state updates
- ❌ Don't create new patterns when existing ones work (follow aiogram/LangGraph patterns)
- ❌ Don't skip async/await - all handlers must be async
- ❌ Don't forget to handle callback query acknowledgments in admin handlers

## Confidence Score: 8/10

This PRP provides comprehensive context for implementing payment confirmation flow with:
✅ All necessary patterns and examples from existing codebase
✅ Detailed integration points with current booking graph 
✅ Specific validation steps that can be executed by AI
✅ Clear task breakdown with implementation order
✅ Anti-patterns to prevent common mistakes

**Potential challenges**: Telegram file handling edge cases and LangGraph state management complexity, but patterns are well-established in codebase.