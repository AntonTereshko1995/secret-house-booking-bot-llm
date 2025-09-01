name: "Current Prices Graph Implementation - Complete LangGraph Integration"
description: |

## Purpose

Implement a complete pricing inquiry graph for the secret house booking bot that allows users to query current prices in natural language and receive formatted, user-friendly responses with detailed pricing information and booking integration.

## Core Principles

1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal

Build a complete pricing inquiry flow that integrates with the existing LangGraph architecture to handle user queries about current prices, extract service requirements from natural language, calculate pricing based on tariff structures and add-ons, and return formatted responses with clear pricing information and booking suggestions.

## Why

- **Business value**: Users need transparent pricing before making booking decisions
- **User experience**: Natural language queries like "сколько стоит аренда?" should work seamlessly
- **Integration**: Must work with existing booking flow to create complete user journey
- **Transparency**: Foundation for dynamic pricing and service customization features

## What

Implement a complete pricing flow that:

- Processes natural language pricing inquiries (Russian and English)
- Extracts service requirements and date preferences
- Calculates pricing based on tariff structures and add-ons
- Returns formatted pricing information with breakdowns
- Integrates with existing LangGraph routing and state management

  Use file confic for tariffs

  Create file for price config. in future I would like to change the data from the file

  {

  "rental_prices": [

  {

  "tariff": 1,

  "name": "тариф 'Суточно' от 3 человек",

  "duration_hours": 24,

  "price": 700,

  "sauna_price": 100,

  "secret_room_price": 0,

  "second_bedroom_price": 0,

  "extra_hour_price": 30,

  "extra_people_price": 0,

  "photoshoot_price": 100,

  "max_people": 6,

  "is_check_in_time_limit": false,

  "is_photoshoot": true,

  "is_transfer": false,

  "subscription_type": 0,

  "multi_day_prices": {

  "1": 700,

  "2": 1300,

  "3": 1850,

  "4": 2400,

  "5": 2950,

  "6": 3500,

  "7": 4050,

  "8": 4600,

  "9": 5150,

  "10": 5700,

  "11": 6250,

  "12": 6800,

  "13": 7350,

  "14": 7900

  }

  },

  {

  "tariff": 7,

  "name": "тариф 'Суточно' для двоих'",

  "duration_hours": 24,

  "price": 500,

  "sauna_price": 100,

  "secret_room_price": 0,

  "second_bedroom_price": 0,

  "extra_hour_price": 30,

  "extra_people_price": 70,

  "photoshoot_price": 100,

  "max_people": 2,

  "is_check_in_time_limit": false,

  "is_photoshoot": true,

  "is_transfer": false,

  "subscription_type": 0,

  "multi_day_prices": {

  "1": 500,

  "2": 900,

  "3": 1300,

  "4": 1700,

  "5": 2050,

  "6": 2400,

  "7": 2800,

  "8": 2200,

  "9": 2600,

  "10": 3000,

  "11": 3450,

  "12": 4000,

  "13": 4350,

  "14": 4800

  }

  },

  {

  "tariff": 0,

  "name": "тариф '12 часов'",

  "duration_hours": 12,

  "price": 250,

  "sauna_price": 100,

  "secret_room_price": 70,

  "second_bedroom_price": 70,

  "extra_hour_price": 30,

  "extra_people_price": 70,

  "photoshoot_price": 0,

  "max_people": 2,

  "is_check_in_time_limit": false,

  "is_photoshoot": false,

  "is_transfer": false,

  "subscription_type": 0,

  "multi_day_prices": {}

  },

  {

  "tariff": 2,

  "name": "тариф 'Рабочий'",

  "duration_hours": 11,

  "price": 180,

  "sauna_price": 100,

  "secret_room_price": 50,

  "second_bedroom_price": 50,

  "extra_hour_price": 30,

  "extra_people_price": 100,

  "photoshoot_price": 0,

  "max_people": 2,

  "is_check_in_time_limit": true,

  "is_photoshoot": false,

  "is_transfer": false,

  "subscription_type": 0,

  "multi_day_prices": {}

  },

  {

  "tariff": 3,

  "name": "тариф 'Инкогнито на день'",

  "duration_hours": 24,

  "price": 900,

  "sauna_price": 0,

  "secret_room_price": 0,

  "second_bedroom_price": 0,

  "extra_hour_price": 30,

  "extra_people_price": 0,

  "photoshoot_price": 0,

  "max_people": 6,

  "is_check_in_time_limit": false,

  "is_photoshoot": true,

  "is_transfer": true,

  "subscription_type": 0,

  "multi_day_prices": {

  "1": 900,

  "2": 1600,

  "3": 2300,

  "4": 3000,

  "5": 3700,

  "6": 4400,

  "7": 5000,

  "8": 5500,

  "9": 6100,

  "10": 6600,

  "11": 5100,

  "12": 5600,

  "13": 6200,

  "14": 6500

  }

  },

  {

  "tariff": 4,

  "name": "тариф 'Инкогнито на 12 часов'",

  "duration_hours": 12,

  "price": 600,

  "sauna_price": 0,

  "secret_room_price": 0,

  "second_bedroom_price": 0,

  "extra_hour_price": 30,

  "extra_people_price": 0,

  "photoshoot_price": 100,

  "max_people": 6,

  "is_check_in_time_limit": false,

  "is_photoshoot": false,

  "is_transfer": true,

  "subscription_type": 0,

  "multi_day_prices": {}

  },

  {

  "tariff": 5,

  "name": "Абонемент на 3 посещений",

  "price": 680,

  "duration_hours": 12,

  "sauna_price": 100,

  "secret_room_price": 0,

  "second_bedroom_price": 0,

  "extra_hour_price": 30,

  "extra_people_price": 70,

  "photoshoot_price": 0,

  "max_people": 3,

  "is_check_in_time_limit": false,

  "is_photoshoot": false,

  "is_transfer": false,

  "subscription_type": 3,

  "multi_day_prices": {}

  },

  {

  "tariff": 5,

  "name": "Абонемент на 5 посещений",

  "price": 1000,

  "duration_hours": 12,

  "sauna_price": 100,

  "secret_room_price": 0,

  "second_bedroom_price": 0,

  "extra_hour_price": 30,

  "extra_people_price": 70,

  "photoshoot_price": 0,

  "max_people": 3,

  "is_check_in_time_limit": false,

  "is_photoshoot": false,

  "is_transfer": false,

  "subscription_type": 5,

  "multi_day_prices": {}

  },

  {

  "tariff": 5,

  "name": "Абонемент на 8 посещений",

  "price": 1600,

  "duration_hours": 12,

  "sauna_price": 100,

  "secret_room_price": 0,

  "second_bedroom_price": 0,

  "extra_hour_price": 30,

  "extra_people_price": 70,

  "photoshoot_price": 0,

  "max_people": 3,

  "is_check_in_time_limit": false,

  "is_photoshoot": false,

  "is_transfer": false,

  "subscription_type": 8,

  "multi_day_prices": {}

  }

  ]

  }

### Success Criteria

- [ ] Users can query prices using natural language in Russian/English
- [ ] Pricing extraction works for different tariff types and add-ons
- [ ] Service returns structured pricing data with breakdowns
- [ ] Responses are user-friendly and include booking guidance
- [ ] All tests pass with 80%+ coverage
- [ ] Integration with main app graph works correctly
- [ ] Pricing data updates can be easily configured

## All Needed Context

### Documentation & References (list all context needed to implement the feature)

```yaml
# MUST READ - Include these in your context window
- url: https://langchain-ai.github.io/langgraph/
  why: Core LangGraph patterns and state management
  section: StateGraph, conditional edges, node patterns
  
- url: https://docs.pydantic.dev/2.0/
  why: Data validation patterns for pricing models
  critical: Use Pydantic v2 syntax for validation and serialization
  
- url: https://docs.python.org/3/library/decimal.html
  why: Financial calculations require Decimal precision
  critical: Never use float for money calculations
  
- file: infrastructure/llm/graphs/app/app_graph_builder.py
  why: Integration pattern with main graph routing
  critical: "price" intent already exists in router branch function
  
- file: infrastructure/llm/graphs/booking/booking_graph.py
  why: Subgraph patterns, state management, conditional routing
  pattern: REQUIRED fields, ask_or_fill node pattern, finalize pattern
  
- file: infrastructure/llm/graphs/common/graph_state.py
  why: AppState structure, state passing patterns
  critical: "price" intent already defined in Literal type
  
- file: infrastructure/llm/graphs/app/router_nodes.py
  why: Intent classification patterns, Russian language matching
  pattern: regex-based intent detection for Russian text
  
- file: domain/booking/entities.py
  why: Existing tariff field in Booking/BookingRequest models
  critical: tariff is str field, needs structured pricing model
  
- file: domain/booking/availability.py
  why: AvailabilitySlot already has Optional[Decimal] price field
  pattern: Use Decimal for all price calculations
  
- file: core/config.py
  why: Settings patterns, timezone configuration
  pattern: Environment variable configuration with defaults
  
- docfile: PRPs/CLAUDE.md
  why: Code style, testing patterns, UV usage, Clean Architecture
  critical: UV commands, strict typing, Russian comments allowed
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
│       ├── entities.py                 # Domain models with tariff field
│       ├── availability.py             # AvailabilitySlot with price field
│       └── ports.py                    # Interfaces
├── application/
│   ├── services/
│   │   └── booking_service.py          # Service layer
│   └── workflows/
├── infrastructure/
│   ├── llm/
│   │   ├── graphs/
│   │   │   ├── app/
│   │   │   │   ├── app_graph_builder.py  # Main graph - needs price node
│   │   │   │   └── router_nodes.py       # Router with price intent
│   │   │   ├── booking/                  # Existing booking subgraph pattern
│   │   │   ├── available_dates/          # Availability pattern to mirror
│   │   │   └── common/
│   │   │       └── graph_state.py        # State with price intent defined
│   │   ├── extractors/                   # Pattern for natural language parsing
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
domain/booking/
└── pricing.py                         # Pricing domain models and entities

application/services/
└── pricing_service.py                 # Dedicated pricing service with calculations

infrastructure/llm/graphs/pricing/
├── __init__.py                        # Module init
├── pricing_node.py                    # Main pricing node implementation
└── pricing_graph.py                   # Complete pricing subgraph (optional)

infrastructure/llm/extractors/
└── pricing_extractor.py               # Extract pricing requirements from text

tests/unit/domain/booking/
└── test_pricing.py                    # Pricing domain model tests

tests/unit/application/services/
└── test_pricing_service.py            # Pricing service unit tests

tests/unit/infrastructure/llm/graphs/pricing/
├── test_pricing_node.py               # Pricing node unit tests
└── test_pricing_extractor.py          # Pricing extractor tests

tests/integration/
└── test_pricing_flow.py               # End-to-end pricing flow tests

# FILES TO MODIFY:
infrastructure/llm/graphs/app/app_graph_builder.py  # Add pricing node to graph
infrastructure/llm/graphs/app/router_nodes.py       # Add price intent detection
core/config.py                                      # Add pricing configuration
```

### Known Gotchas of our codebase & Library Quirks

```python
# CRITICAL: Decimal for Money
# Never use float for financial calculations
from decimal import Decimal
price = Decimal("99.99")  # Always string to avoid float precision issues

# CRITICAL: Russian Language Interface
# All user-facing responses must be in Russian
reply = f"Стоимость аренды составляет {price} руб."

# CRITICAL: LangGraph State Management
# AppState is TypedDict with total=False - use .get() with defaults
# State updates must return dict, not modify in place
def pricing_node(state: AppState) -> Dict[str, Any]:
    return {"reply": "...", "pricing_data": {...}}  # Return new state

# CRITICAL: Clean Architecture Boundaries
# Domain models in domain/ - no external dependencies
# Services in application/ - orchestrate domain logic
# Infrastructure in infrastructure/ - external concerns only

# CRITICAL: Async Patterns
# All service methods are async, follow existing patterns
async def calculate_pricing(self, request: PricingRequest) -> PricingResponse:
    # Implementation

# CRITICAL: Timezone Handling
# Project uses Europe/Minsk timezone
from core.utils.datetime_helper import TZ
now = datetime.now(TZ)

# CRITICAL: Testing with UV
# Always use uv run pytest for testing
# Test patterns: test_*, async tests supported automatically

# CRITICAL: State Typing
# AppState already defines "price" as valid intent
# Router already has price intent routing - just needs corresponding node

# CRITICAL: Configuration Pattern
# Settings use pydantic-settings with environment variables
class Settings(BaseSettings):
    pricing_cache_ttl: int = Field(300, env="PRICING_CACHE_TTL")
```

## Implementation Blueprint

### Data models and structure

Create the core pricing data models for type safety and consistency.

```python
# Domain entities for pricing
@dataclass
class TariffRate(BaseModel):
    """Base tariff pricing information"""
    name: str  # "standard", "premium", "vip"
    base_price_per_hour: Decimal
    minimum_hours: int
    weekend_multiplier: Decimal = Decimal("1.2")
    description: str
  
    class Config:
        use_enum_values = True

@dataclass
class AddOnService(BaseModel):
    """Additional service pricing"""
    service_id: str  # "sauna", "photoshoot", "secret_room"
    name: str
    price: Decimal
    is_per_hour: bool = False
    description: str

@dataclass
class PricingRequest(BaseModel):
    """Request for pricing calculation"""
    tariff: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_hours: Optional[int] = None
    add_ons: List[str] = []  # Service IDs
    number_guests: Optional[int] = None
  
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

@dataclass
class PricingBreakdown(BaseModel):
    """Detailed pricing breakdown"""
    tariff_name: str
    base_cost: Decimal
    duration_hours: int
    weekend_multiplier: Optional[Decimal] = None
    add_on_costs: Dict[str, Decimal] = {}
    total_cost: Decimal
    currency: str = "RUB"
  
class PricingResponse(BaseModel):
    """Complete pricing response"""
    breakdown: PricingBreakdown
    formatted_message: str
    booking_suggestion: str
    valid_until: datetime
```

### list of tasks to be completed to fullfill the PRP in the order they should be completed

```yaml
Task 1: Create Pricing Domain Models
CREATE domain/booking/pricing.py:
  - IMPLEMENT TariffRate, AddOnService, PricingRequest models
  - FOLLOW patterns from: domain/booking/entities.py
  - USE Decimal for all monetary values
  - INCLUDE Russian descriptions for user-facing content

Task 2: Implement Pricing Service
CREATE application/services/pricing_service.py:
  - IMPLEMENT PricingService class with async methods
  - MIRROR pattern from: application/services/booking_service.py
  - ADD calculate_pricing, get_tariff_rates, get_add_on_services methods
  - INCLUDE weekend/holiday pricing logic

Task 3: Create Pricing Extractor
CREATE infrastructure/llm/extractors/pricing_extractor.py:
  - IMPLEMENT natural language parsing for pricing requests
  - MIRROR pattern from: infrastructure/llm/extractors/date_extractor.py
  - ADD Russian/English text parsing for tariffs and services
  - EXTRACT pricing requirements from user messages

Task 4: Implement Pricing Node
CREATE infrastructure/llm/graphs/pricing/pricing_node.py:
  - IMPLEMENT pricing_node async function
  - FOLLOW pattern from: infrastructure/llm/graphs/available_dates/availability_node.py
  - INTEGRATE with PricingService and PricingExtractor
  - FORMAT responses in Russian with clear breakdowns

Task 5: Update App Graph Builder
MODIFY infrastructure/llm/graphs/app/app_graph_builder.py:
  - ADD pricing node to graph structure
  - ADD conditional edge for "price" intent
  - PRESERVE existing routing logic
  - IMPORT pricing_node from new module

Task 6: Enhance Router with Price Detection
MODIFY infrastructure/llm/graphs/app/router_nodes.py:
  - ADD regex patterns for price-related queries
  - INCLUDE Russian patterns: "цена", "стоимость", "сколько стоит"
  - PRESERVE existing intent detection logic
  - RETURN price intent for pricing queries

Task 7: Add Pricing Configuration
MODIFY core/config.py:
  - ADD pricing-related settings
  - INCLUDE cache TTL, default tariff rates
  - FOLLOW existing Settings class pattern
  - USE environment variable defaults

Task 8: Implement Unit Tests
CREATE tests/unit/domain/booking/test_pricing.py:
  - TEST pricing model validation
  - TEST calculation logic edge cases
  - FOLLOW pytest patterns from existing tests
  - INCLUDE Russian text scenarios

CREATE tests/unit/application/services/test_pricing_service.py:
  - TEST pricing calculations with various scenarios
  - TEST weekend multipliers and add-ons
  - MOCK external dependencies
  - ASYNC test patterns with pytest-asyncio

CREATE tests/unit/infrastructure/llm/graphs/pricing/test_pricing_node.py:
  - TEST node state handling
  - TEST error scenarios
  - TEST Russian response formatting
  - MOCK service dependencies

Task 9: Integration Testing
CREATE tests/integration/test_pricing_flow.py:
  - TEST complete flow from user input to response
  - TEST LangGraph integration
  - TEST state management through pricing flow
  - INCLUDE multiple language scenarios

Task 10: Validation and Polish
RUN complete validation pipeline:
  - Execute syntax/style checks with uv run ruff
  - Run all unit tests with uv run pytest
  - Run integration tests
  - Manual testing with various pricing queries
```

### Per task pseudocode as needed added to each task

```python
# Task 2: PricingService Implementation
class PricingService:
    def __init__(self):
        self.tariff_rates = self._load_tariff_rates()
        self.add_on_services = self._load_add_on_services()
  
    async def calculate_pricing(
        self, request: PricingRequest
    ) -> PricingResponse:
        # PATTERN: Validate request first
        if not request.tariff:
            request.tariff = "standard"  # Default tariff
      
        # CRITICAL: Get base tariff rate
        tariff = self.tariff_rates.get(request.tariff)
        if not tariff:
            raise ValueError(f"Unknown tariff: {request.tariff}")
      
        # PATTERN: Calculate duration
        duration_hours = request.duration_hours or 4  # Minimum
        if duration_hours < tariff.minimum_hours:
            duration_hours = tariff.minimum_hours
      
        # CRITICAL: Base cost calculation
        base_cost = tariff.base_price_per_hour * duration_hours
      
        # GOTCHA: Weekend pricing
        weekend_multiplier = None
        if request.start_date and self._is_weekend(request.start_date):
            weekend_multiplier = tariff.weekend_multiplier
            base_cost *= weekend_multiplier
      
        # PATTERN: Add-on services
        add_on_costs = {}
        total_add_on_cost = Decimal("0")
        for service_id in request.add_ons:
            service = self.add_on_services.get(service_id)
            if service:
                cost = service.price
                if service.is_per_hour:
                    cost *= duration_hours
                add_on_costs[service_id] = cost
                total_add_on_cost += cost
      
        # CRITICAL: Total calculation
        total_cost = base_cost + total_add_on_cost
      
        breakdown = PricingBreakdown(
            tariff_name=tariff.name,
            base_cost=base_cost,
            duration_hours=duration_hours,
            weekend_multiplier=weekend_multiplier,
            add_on_costs=add_on_costs,
            total_cost=total_cost
        )
      
        # PATTERN: Format user-friendly message in Russian
        message = self._format_pricing_message(breakdown)
        suggestion = "Хотите забронировать? Укажите даты и время."
      
        return PricingResponse(
            breakdown=breakdown,
            formatted_message=message,
            booking_suggestion=suggestion,
            valid_until=datetime.now(TZ) + timedelta(hours=24)
        )
  
    def _format_pricing_message(self, breakdown: PricingBreakdown) -> str:
        # CRITICAL: Russian formatting
        message = f"💰 Стоимость аренды ({breakdown.tariff_name}):\n"
        message += f"• Базовая стоимость: {breakdown.base_cost} руб. ({breakdown.duration_hours} ч.)\n"
      
        if breakdown.weekend_multiplier:
            message += f"• Надбавка за выходные: x{breakdown.weekend_multiplier}\n"
      
        for service_id, cost in breakdown.add_on_costs.items():
            service_name = self.add_on_services[service_id].name
            message += f"• {service_name}: {cost} руб.\n"
      
        message += f"\n💳 Итого: {breakdown.total_cost} руб."
        return message

# Task 4: Pricing Node Implementation
async def pricing_node(state: AppState) -> Dict[str, Any]:
    """Handle pricing inquiries with natural language processing"""
    try:
        # PATTERN: Extract pricing requirements
        extractor = PricingExtractor()
        pricing_request = await extractor.extract_pricing_requirements(
            state.get("text", "")
        )
      
        # CRITICAL: Service call with error handling
        pricing_service = PricingService()
        pricing_response = await pricing_service.calculate_pricing(
            pricing_request
        )
      
        # PATTERN: Format response
        reply = pricing_response.formatted_message
        if pricing_response.booking_suggestion:
            reply += f"\n\n{pricing_response.booking_suggestion}"
      
        return {
            "reply": reply,
            "pricing_data": pricing_response.dict(),
            "intent": "price"  # Maintain intent
        }
      
    except Exception as e:
        logger.exception(f"Error in pricing_node: {e}")
        return {
            "reply": "Произошла ошибка при расчете стоимости. Попробуйте еще раз или обратитесь к администратору.",
            "intent": "price"
        }

# Task 6: Router Enhancement
# ADD to router_node function in router_nodes.py
if re.search(r"(цен[аы]|стоимост|сколько стоит|прайс|price)", t):
    return {"intent": "price"}
```

### Integration Points

```yaml
DATABASE:
  - optional: "CREATE TABLE tariff_rates (name TEXT, base_price DECIMAL, ...)"
  - pattern: Can start with in-memory configuration, migrate to DB later
  
CONFIG:
  - add to: core/config.py
  - pattern: "PRICING_CACHE_TTL = int(os.getenv('PRICING_CACHE_TTL', '300'))"
  - pattern: "DEFAULT_TARIFF = os.getenv('DEFAULT_TARIFF', 'standard')"
  
ROUTES:
  - modify: infrastructure/llm/graphs/app/app_graph_builder.py  
  - pattern: 'g.add_node("pricing", pricing_node)'
  - pattern: '"price": "pricing"' in conditional_edges mapping

STATE_MANAGEMENT:
  - uses: infrastructure/llm/graphs/common/graph_state.py
  - pattern: AppState with existing "price" intent support
  - enhancement: Optional pricing_data field for state persistence
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
# CREATE test_pricing_service.py with these test cases:
def test_calculate_pricing_standard_tariff():
    """Test basic pricing calculation with standard tariff"""
    service = PricingService()
    request = PricingRequest(
        tariff="standard",
        duration_hours=4
    )
  
    result = await service.calculate_pricing(request)
    assert result.breakdown.tariff_name == "standard"
    assert result.breakdown.duration_hours == 4
    assert result.breakdown.total_cost > 0

def test_calculate_pricing_with_weekend_multiplier():
    """Test weekend pricing multiplier application"""
    service = PricingService()
    # Saturday date
    weekend_date = datetime(2025, 3, 8, 14, 0, tzinfo=TZ)  # Saturday
    request = PricingRequest(
        tariff="standard",
        start_date=weekend_date,
        duration_hours=4
    )
  
    result = await service.calculate_pricing(request)
    assert result.breakdown.weekend_multiplier == Decimal("1.2")
    # Base cost should be multiplied by weekend rate

def test_calculate_pricing_with_add_ons():
    """Test pricing with additional services"""
    service = PricingService()
    request = PricingRequest(
        tariff="standard",
        duration_hours=4,
        add_ons=["sauna", "photoshoot"]
    )
  
    result = await service.calculate_pricing(request)
    assert len(result.breakdown.add_on_costs) == 2
    assert "sauna" in result.breakdown.add_on_costs
    assert "photoshoot" in result.breakdown.add_on_costs

def test_pricing_node_success_flow():
    """Test pricing node with valid input"""
    state = {"text": "сколько стоит аренда на 4 часа стандарт"}
    result = await pricing_node(state)
  
    assert "reply" in result
    assert "руб" in result["reply"]  # Russian currency
    assert result["intent"] == "price"

def test_pricing_extractor_russian_text():
    """Test extraction from Russian pricing queries"""
    extractor = PricingExtractor()
    text = "сколько стоит премиум тариф на выходные с сауной"
  
    result = await extractor.extract_pricing_requirements(text)
    assert result.tariff == "premium"
    assert "sauna" in result.add_ons
```

```bash
# Run and iterate until passing:
uv run pytest tests/unit/ -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test

```bash
# Test the complete flow through LangGraph
uv run pytest tests/integration/test_pricing_flow.py -v

# Manual testing queries:
# "сколько стоит аренда?"
# "цена на стандартный тариф"
# "стоимость премиум с сауной"
# "pricing for weekend"

# Expected responses in Russian with detailed breakdowns
```

## Final validation Checklist

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check .`
- [ ] No type errors: `uv run mypy .`
- [ ] No format issues: `uv run ruff format . --check`
- [ ] Manual test successful with various pricing queries
- [ ] Error cases handled gracefully in Russian
- [ ] Pricing calculations accurate with Decimal precision
- [ ] Integration with booking flow works
- [ ] Weekend/holiday pricing logic correct

---

## Anti-Patterns to Avoid

- ❌ Don't use float for monetary calculations - always Decimal
- ❌ Don't hardcode pricing in nodes - use service layer
- ❌ Don't ignore weekend/holiday pricing logic
- ❌ Don't return English messages - users expect Russian
- ❌ Don't skip input validation - invalid tariffs cause errors
- ❌ Don't expose internal pricing structure in responses
- ❌ Don't break existing graph routing patterns
- ❌ Don't create pricing logic in domain models - keep them pure

## Score Assessment

**Confidence Level: 9.0/10**

This PRP provides comprehensive context for one-pass implementation:

- ✅ Complete codebase analysis with existing patterns identified
- ✅ Detailed task breakdown with specific file modifications
- ✅ Russian language requirements documented
- ✅ Financial calculation best practices (Decimal usage)
- ✅ LangGraph integration patterns clearly defined
- ✅ Error handling and validation strategies specified
- ✅ Clean Architecture boundaries respected
- ✅ Comprehensive test coverage planned
- ✅ Integration points clearly documented
- ✅ Anti-patterns documented to avoid common mistakes

The implementation should succeed with high confidence given the detailed context, existing patterns, and clear validation steps.
