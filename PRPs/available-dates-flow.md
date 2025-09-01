name: "Available Dates Flow Implementation - Complete LangGraph Integration"
description: |

## Purpose
Implement a complete available dates flow for the secret house booking bot that allows users to query availability in natural language and receive formatted, user-friendly responses with booking integration.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
Build a complete available dates flow that integrates with the existing LangGraph architecture to handle user queries about availability, extract date/time information from natural language, query the booking service, and return formatted responses with clear availability information and booking suggestions.

## Why
- **Business value**: Users need to check availability before booking
- **User experience**: Natural language queries like "what dates are available in March?" should work seamlessly
- **Integration**: Must work with existing booking flow to create complete user journey
- **Scalability**: Foundation for future availability features (filters, suggestions, etc.)

## What
Implement a complete availability flow that:
- Processes natural language date queries (Russian and English)
- Extracts date ranges with timezone handling
- Queries booking service for availability
- Returns formatted availability information
- Integrates with existing LangGraph routing and state management

### Success Criteria
- [ ] Users can query availability using natural language in Russian/English
- [ ] Date extraction works for relative dates ("next month", "current month")
- [ ] Date extraction works for specific months ("март", "march")
- [ ] Service returns structured availability data
- [ ] Responses are user-friendly and include booking guidance
- [ ] All tests pass with 80%+ coverage
- [ ] Integration with main app graph works correctly

## All Needed Context

### Documentation & References (list all context needed to implement the feature)
```yaml
# MUST READ - Include these in your context window
- url: https://langchain-ai.github.io/langgraph/
  why: Core LangGraph patterns and state management
  section: StateGraph, conditional edges, subgraph patterns
  
- url: https://docs.python.org/3/library/datetime.html
  why: Timezone handling best practices for booking systems
  critical: Always use UTC for storage, timezone-aware objects
  
- url: https://howik.com/python-datetime-best-practices
  why: 2025 Python datetime best practices for booking systems
  section: Timezone handling, DST considerations, UTC storage
  
- file: infrastructure/llm/graphs/app/app_graph_builder.py
  why: Integration pattern with main graph routing, existing availability node
  
- file: infrastructure/llm/graphs/booking/booking_graph.py
  why: Subgraph patterns, state management, conditional routing
  
- file: infrastructure/llm/graphs/common/graph_state.py
  why: AppState structure, state passing patterns
  
- file: infrastructure/llm/extractors/date_extractor.py
  why: Existing date extraction patterns, Russian/English handling
  critical: Already handles month boundaries, timezone (Europe/Minsk)
  
- file: application/services/booking_service.py
  why: Service patterns, async methods, availability checking
  critical: Missing availability_for_period method needs implementation
  
- file: core/config.py
  why: Settings patterns, timezone configuration
  
- docfile: PRPs/CLAUDE.md
  why: Code style, testing patterns, UV usage, Clean Architecture
```

### Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase
```bash
/Users/a/secret-house-booking-bot-llm/
├── apps/
│   └── telegram_bot/
│       ├── main.py                     # Bot entry point
│       ├── handlers/
│       ├── middlewares/
│       └── adapters/
├── core/
│   ├── config.py                       # Settings with timezone
│   ├── logging.py                      # Structured logging
│   └── utils/
├── domain/
│   └── booking/
│       ├── entities.py                 # Domain models
│       └── ports.py                    # Interfaces
├── application/
│   ├── services/
│   │   └── booking_service.py          # Service layer - needs availability_for_period
│   └── workflows/
├── infrastructure/
│   ├── llm/
│   │   ├── graphs/
│   │   │   ├── app/
│   │   │   │   └── app_graph_builder.py  # Main graph with availability node
│   │   │   ├── booking/                  # Existing booking subgraph pattern
│   │   │   ├── available_dates/
│   │   │   │   └── availability_node.py  # Basic implementation exists
│   │   │   └── common/
│   │   │       └── graph_state.py        # State management
│   │   ├── extractors/
│   │   │   └── date_extractor.py         # Date extraction - has month_bounds_from_text
│   │   └── clients/
│   │       └── openai_client.py
│   ├── db/                             # Database layer
│   ├── kv/                             # Redis for state
│   └── vector/                         # ChromaDB
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

### Desired Codebase tree with files to be added and responsibility of file
```bash
# NEW FILES TO CREATE:
infrastructure/llm/graphs/available_dates/
└── available_dates_graph.py           # Complete subgraph (optional enhancement)

application/services/
└── availability_service.py            # Dedicated availability service

tests/unit/infrastructure/llm/graphs/available_dates/
├── test_availability_node.py          # Node unit tests
└── test_date_extractor.py             # Date extractor tests

tests/unit/application/services/
└── test_availability_service.py       # Service unit tests

tests/integration/
└── test_available_dates_flow.py       # End-to-end flow tests

# FILES TO MODIFY:
application/services/booking_service.py  # Add availability_for_period method
infrastructure/llm/graphs/available_dates/availability_node.py  # Complete implementation
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: Timezone handling
# Project uses Europe/Minsk timezone (see core/utils/datetime_helper.py)
TZ = pytz.timezone("Europe/Minsk")
# Always use timezone-aware datetime objects, store in UTC

# CRITICAL: LangGraph State Management
# AppState dict-like structure, use .get() with defaults
# State is immutable - return new dict updates

# CRITICAL: Service Dependencies
# BookingService currently has commented out dependencies
# Need to implement availability_for_period method without breaking existing code

# CRITICAL: Russian Language Support
# DateExtractor already handles Russian months
# Response messages should be in Russian (user expectation)

# CRITICAL: Clean Architecture
# Don't put business logic in graph nodes - keep them thin
# Service layer should handle complex availability logic
# Domain entities for availability data structures

# CRITICAL: Testing Requirements
# Use pytest with async support (asyncio_mode = "auto")
# UV command: uv run pytest
# Coverage target: 80%+

# CRITICAL: Error Handling
# Always handle timezone conversion errors
# Handle invalid date ranges gracefully
# Return user-friendly error messages in Russian
```

## Implementation Blueprint

### Data models and structure

Create the core data models, we ensure type safety and consistency.
```python
# Domain entities for availability
@dataclass
class AvailabilitySlot:
    date: datetime
    is_available: bool
    booking_id: Optional[UUID] = None
    price: Optional[Decimal] = None

@dataclass  
class AvailabilityPeriod:
    start_date: datetime
    end_date: datetime
    slots: List[AvailabilitySlot]
    total_available_days: int
    
# Service request/response models
class AvailabilityRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    user_timezone: str = "Europe/Minsk"

class AvailabilityResponse(BaseModel):
    period: AvailabilityPeriod
    message: str
    suggestions: List[str] = []
```

### list of tasks to be completed to fullfill the PRP in the order they should be completed

```yaml
Task 1: Implement AvailabilityService
MODIFY application/services/booking_service.py:
  - ADD availability_for_period method
  - PRESERVE existing method signatures
  - FOLLOW async patterns from existing methods

CREATE application/services/availability_service.py:
  - IMPLEMENT dedicated availability service
  - MIRROR pattern from: application/services/booking_service.py
  - INCLUDE timezone handling and date validation

Task 2: Enhance Date Extraction
MODIFY infrastructure/llm/extractors/date_extractor.py:
  - ADD specific date parsing (not just months)
  - ADD date range parsing ("15-20 марта")
  - PRESERVE existing month_bounds_from_text method
  - ADD validation for date ranges

Task 3: Complete Availability Node
MODIFY infrastructure/llm/graphs/available_dates/availability_node.py:
  - IMPLEMENT complete availability logic
  - ADD error handling and validation
  - FORMAT user-friendly responses in Russian
  - INTEGRATE with enhanced date extractor

Task 4: Add Domain Models
CREATE domain/booking/availability.py:
  - ADD AvailabilitySlot and AvailabilityPeriod entities
  - FOLLOW patterns from: domain/booking/entities.py
  - INCLUDE type hints and validation

Task 5: Implement Unit Tests
CREATE tests/unit/infrastructure/llm/graphs/available_dates/test_availability_node.py:
  - TEST date extraction edge cases
  - TEST service integration
  - TEST error handling scenarios
  - MIRROR test patterns from existing booking tests

CREATE tests/unit/application/services/test_availability_service.py:
  - TEST availability checking logic
  - TEST timezone handling
  - TEST date validation
  - FOLLOW pytest async patterns

Task 6: Integration Testing
CREATE tests/integration/test_available_dates_flow.py:
  - TEST full flow from user input to response
  - TEST LangGraph integration
  - TEST state management
  - INCLUDE multiple language scenarios (Russian/English)

Task 7: Validation and Polish
RUN complete validation pipeline:
  - Execute syntax/style checks
  - Run all unit tests
  - Run integration tests
  - Manual testing with different date queries
```

### Per task pseudocode as needed added to each task

```python
# Task 1: AvailabilityService Implementation
class AvailabilityService:
    async def get_availability_for_period(
        self, start_date: datetime, end_date: datetime
    ) -> AvailabilityPeriod:
        # PATTERN: Always validate dates first (timezone-aware)
        validated_start = self._ensure_timezone_aware(start_date)
        validated_end = self._ensure_timezone_aware(end_date)
        
        # CRITICAL: Query existing bookings for period
        # Mock implementation - replace with real repository query
        existing_bookings = await self._get_bookings_for_period(
            validated_start, validated_end
        )
        
        # PATTERN: Generate day-by-day availability
        slots = []
        current_date = validated_start.date()
        while current_date <= validated_end.date():
            is_booked = any(
                booking.start_date.date() <= current_date <= booking.end_date.date()
                for booking in existing_bookings
            )
            slots.append(AvailabilitySlot(
                date=datetime.combine(current_date, datetime.min.time(), TZ),
                is_available=not is_booked
            ))
            current_date += timedelta(days=1)
        
        return AvailabilityPeriod(
            start_date=validated_start,
            end_date=validated_end,
            slots=slots,
            total_available_days=sum(1 for slot in slots if slot.is_available)
        )

# Task 3: Enhanced Availability Node
async def availability_node(s: AppState) -> Dict[str, Any]:
    # PATTERN: Extract and validate dates
    try:
        month_start, month_end, matched_label = date_extractor.month_bounds_from_text(
            s.get("text", "")
        )
        
        # CRITICAL: Service call with error handling
        availability_service = AvailabilityService()
        availability_data = await availability_service.get_availability_for_period(
            month_start, month_end
        )
        
        # PATTERN: Format user-friendly response in Russian
        available_count = availability_data.total_available_days
        total_days = len(availability_data.slots)
        
        if available_count == 0:
            reply = f"К сожалению, на {matched_label} нет свободных дней."
        elif available_count == total_days:
            reply = f"Отлично! Все {total_days} дней в {matched_label} свободны для бронирования."
        else:
            reply = f"В {matched_label} свободно {available_count} из {total_days} дней."
        
        # GOTCHA: Include booking suggestions
        if available_count > 0:
            reply += "\n\nХотите забронировать? Напишите даты и время."
        
        return {"reply": reply, "availability_data": availability_data}
        
    except Exception as e:
        logger.exception(f"Error in availability_node: {e}")
        return {"reply": "Произошла ошибка при проверке доступности. Попробуйте еще раз."}
```

### Integration Points
```yaml
DATABASE:
  - query: "SELECT * FROM bookings WHERE start_date <= ? AND end_date >= ?"
  - index: "CREATE INDEX idx_booking_dates ON bookings(start_date, end_date)"
  
CONFIG:
  - uses: core/config.py timezone settings
  - pattern: TZ = pytz.timezone(settings.timezone)
  
ROUTES:
  - integrates: infrastructure/llm/graphs/app/app_graph_builder.py  
  - pattern: existing "availability" node routing in branch() function

STATE_MANAGEMENT:
  - uses: infrastructure/llm/graphs/common/graph_state.py
  - pattern: AppState with .get() method for safe access
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
uv run ruff check . --fix              # Auto-fix what's possible
uv run ruff format .                   # Format code
uv run mypy .                          # Type checking

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests each new feature/file/function use existing test patterns
```python
# CREATE test_availability_service.py with these test cases:
def test_get_availability_for_period_all_available():
    """Test when all dates in period are available"""
    service = AvailabilityService()
    start = datetime(2025, 3, 1, tzinfo=TZ)
    end = datetime(2025, 3, 31, tzinfo=TZ)
    
    result = await service.get_availability_for_period(start, end)
    assert result.total_available_days == 31
    assert all(slot.is_available for slot in result.slots)

def test_get_availability_for_period_with_bookings():
    """Test availability with existing bookings"""
    # Mock existing booking for March 15-17
    with mock.patch.object(service, '_get_bookings_for_period') as mock_bookings:
        mock_bookings.return_value = [mock_booking_march_15_17]
        result = await service.get_availability_for_period(start, end)
        assert result.total_available_days == 28  # 31 - 3 booked days

def test_date_extractor_specific_dates():
    """Test extraction of specific date ranges"""
    extractor = DateExtractor()
    result = extractor.extract_date_range("15-20 марта")
    assert result.start_date.day == 15
    assert result.end_date.day == 20
    assert result.start_date.month == 3

def test_availability_node_error_handling():
    """Test graceful error handling in availability node"""
    state = {"text": "invalid date query"}
    result = await availability_node(state)
    assert "ошибка" in result["reply"].lower()
```

```bash
# Run and iterate until passing:
uv run pytest tests/unit/ -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Test the complete flow through LangGraph
uv run pytest tests/integration/test_available_dates_flow.py -v

# Manual testing queries:
# "какие даты свободны в марте?"
# "что доступно в следующем месяце?"
# "available dates in March"
# "15-20 марта свободно?"

# Expected responses in Russian with availability information
```

## Final validation Checklist
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check .`
- [ ] No type errors: `uv run mypy .`
- [ ] No format issues: `uv run ruff format . --check`
- [ ] Manual test successful with various date queries
- [ ] Error cases handled gracefully in Russian
- [ ] Logs are informative but not verbose
- [ ] Integration with booking flow works
- [ ] Timezone handling is correct (Europe/Minsk)

---

## Anti-Patterns to Avoid
- ❌ Don't put business logic in graph nodes - keep them thin
- ❌ Don't ignore timezone conversion - always use timezone-aware objects
- ❌ Don't hardcode dates or times - use service configuration
- ❌ Don't return English messages - users expect Russian
- ❌ Don't skip date validation - invalid dates cause runtime errors
- ❌ Don't mock real availability data in production paths
- ❌ Don't break existing booking service interface

## Score Assessment
**Confidence Level: 8.5/10**

This PRP provides comprehensive context for one-pass implementation:
- ✅ Complete codebase analysis with existing patterns identified
- ✅ Detailed task breakdown with specific file modifications
- ✅ Russian language requirements documented
- ✅ Timezone handling best practices included
- ✅ Error handling patterns specified
- ✅ Integration points clearly defined
- ✅ Validation loops are executable
- ✅ Anti-patterns documented to avoid common mistakes

The implementation should succeed with this level of context and guidance.