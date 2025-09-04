name: "FAQ Graph Flow Implementation - Complete LangGraph Integration"
description: |

## Purpose

Implement a complete FAQ graph flow for The Secret House booking bot that provides intelligent, natural language responses to user questions about the house, services, pricing, and booking process. The system will use an intelligent question-answering approach with fallback to human assistance.

## Core Principles

1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal

Build a complete LLM-powered FAQ handling system that integrates with the existing LangGraph architecture to intelligently answer user questions about The Secret House using ChatGPT/OpenAI. The system will use the existing OpenAI client to generate natural, conversational responses about house amenities, pricing, booking process, and policies. It should handle Russian language queries naturally and provide helpful, engaging responses while directing users to appropriate bot functions when needed.

## Why

- **Business value**: Reduces support load by intelligently answering common questions
- **User experience**: Provides immediate, accurate answers to user queries in Russian
- **Integration**: Seamlessly integrates with existing booking, pricing, and availability flows
- **Scalability**: Foundation for advanced FAQ features like learning from interactions
- **Customer satisfaction**: Provides 24/7 intelligent support with consistent, branded responses

## What

Implement a complete LLM-powered FAQ flow that:

- Uses ChatGPT/OpenAI to generate intelligent, contextual responses
- Processes natural language questions in Russian (primary) and English  
- Provides dynamic responses using the detailed house information as context
- Maintains conversational, friendly, and slightly playful tone through LLM prompts
- Uses AI to intelligently direct users to appropriate bot functions (booking, pricing, availability)
- Handles edge cases and unknown questions gracefully with LLM flexibility
- Integrates with existing LangGraph routing and OpenAI client infrastructure
- Supports natural conversational flow and contextual follow-up questions

### Success Criteria

- [ ] LLM generates accurate, contextual responses using house information as context
- [ ] System maintains conversational flow with natural follow-up capabilities  
- [ ] AI responses maintain the specified tone: friendly, confident, slightly playful, respectful
- [ ] LLM intelligently directs users to booking, pricing, and availability functions when appropriate
- [ ] ChatGPT handles unknown/complex questions gracefully with natural language
- [ ] All tests pass with 80%+ coverage including LLM response validation
- [ ] Integration with existing OpenAI client and LangGraph works correctly
- [ ] Russian language responses are natural, engaging, and grammatically correct

## All Needed Context

### Documentation & References (list all context needed to implement the feature)

```yaml
# MUST READ - Include these in your context window
- url: https://langchain-ai.github.io/langgraph/
  why: Core LangGraph patterns and state management
  section: StateGraph, conditional edges, node patterns, memory persistence
  
- url: https://langchain-ai.github.io/langgraph/tutorials/customer-support/customer-support/
  why: Customer support chatbot patterns and implementation approaches
  critical: FAQ handling, state management, tool integration patterns
  
- url: https://docs.python.org/3/library/re.html
  why: Regular expression patterns for Russian text matching
  critical: Unicode handling for Cyrillic characters
  
- file: infrastructure/llm/graphs/app/app_graph_builder.py
  why: Integration pattern with main graph routing
  critical: "faq" intent routing currently goes to fallback_node
  
- file: infrastructure/llm/graphs/app/router_nodes.py
  why: Intent classification patterns, Russian language matching
  pattern: Existing regex patterns for Russian text analysis
  
- file: infrastructure/llm/graphs/common/graph_state.py
  why: AppState structure, state passing patterns
  critical: "faq" intent already defined in Literal type
  
- file: infrastructure/llm/clients/openai_client.py
  why: Existing OpenAI client integration patterns
  critical: get_llm() function, ChatOpenAI setup with model configuration
  
- file: infrastructure/llm/extractors/booking_extractor.py
  why: LLM usage patterns, async ainvoke calls, prompt templates
  pattern: self.llm.ainvoke(msg) usage, prompt.ainvoke() patterns
  
- file: infrastructure/llm/graphs/fallback/fallback_node.py
  why: Current fallback implementation that needs to be enhanced/replaced
  pattern: Simple response structure, error handling
  
- file: infrastructure/llm/graphs/available_dates/availability_node.py
  why: Node implementation patterns, error handling, Russian responses
  pattern: Service integration, structured responses, logging
  
- file: core/config.py
  why: Settings patterns, environment configuration
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
│   ├── config.py                       # Settings configuration
│   ├── logging.py                      # Structured logging
│   └── utils/
├── domain/
│   └── booking/
│       ├── entities.py                 # Domain models
│       └── ports.py                    # Interfaces
├── application/
│   ├── services/
│   │   └── booking_service.py          # Service layer
│   └── workflows/
├── infrastructure/
│   ├── llm/
│   │   ├── graphs/
│   │   │   ├── app/
│   │   │   │   ├── app_graph_builder.py  # Main graph - needs FAQ node
│   │   │   │   └── router_nodes.py       # Router with FAQ intent detection
│   │   │   ├── booking/                  # Booking subgraph pattern
│   │   │   ├── available_dates/          # Availability pattern to reference
│   │   │   ├── pricing/                  # Pricing pattern to reference
│   │   │   ├── fallback/                 # Current fallback - to enhance/replace
│   │   │   └── common/
│   │   │       └── graph_state.py        # State with FAQ intent defined
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
domain/faq/
├── __init__.py                        # Module init
└── entities.py                        # FAQ domain models (Question, Answer, Category)

application/services/
└── faq_service.py                     # FAQ service for question matching and response generation

infrastructure/llm/graphs/faq/
├── __init__.py                        # Module init
├── faq_node.py                        # Main FAQ node implementation
└── faq_patterns.py                    # Question pattern matching and categorization

tests/unit/domain/faq/
└── test_faq_entities.py               # FAQ domain model tests

tests/unit/application/services/
└── test_faq_service.py                # FAQ service unit tests

tests/unit/infrastructure/llm/graphs/faq/
├── test_faq_node.py                   # FAQ node unit tests
└── test_faq_patterns.py               # FAQ pattern matching tests

tests/integration/
└── test_faq_flow.py                   # End-to-end FAQ flow tests

# FILES TO MODIFY:
infrastructure/llm/graphs/app/app_graph_builder.py  # Replace fallback with FAQ node
infrastructure/llm/graphs/app/router_nodes.py       # Enhance FAQ intent detection
core/config.py                                      # Add FAQ configuration settings

# FILES TO POTENTIALLY ENHANCE:
infrastructure/llm/graphs/fallback/fallback_node.py # Keep for true unknown intents
```

### Known Gotchas of our codebase & Library Quirks

```python
# CRITICAL: LLM Integration Pattern
# Use existing OpenAI client from infrastructure/llm/clients/openai_client.py
from infrastructure.llm.clients.openai_client import get_llm
llm = get_llm()  # Returns configured ChatOpenAI instance

# CRITICAL: LLM Async Usage Pattern  
# Follow patterns from booking_extractor.py for LLM calls
response = await llm.ainvoke([HumanMessage(content=prompt)])
answer = response.content

# CRITICAL: Russian Language LLM Prompts
# LLM prompts must specify Russian language and tone requirements
# Include house information as context in system prompt

# CRITICAL: LangGraph State Management
# AppState is TypedDict with total=False - use .get() with defaults
# State updates must return dict, not modify in place
def faq_node(state: AppState) -> Dict[str, Any]:
    return {"reply": "...", "faq_context": {...}}  # Return new state

# CRITICAL: Clean Architecture Boundaries
# Domain models in domain/ - no external dependencies
# Services in application/ - orchestrate domain logic  
# Infrastructure in infrastructure/ - external concerns only

# CRITICAL: Tone and Style Requirements
# Must be: дружелюбным, уверенным и немного игривым, но всегда уважительным
# Emphasize: приватность, комфорт и уникальность атмосферы дома
# Always suggest booking when appropriate

# CRITICAL: Bot Function Integration
# Direct users to specific bot functions:
# - "перейди в пункт меню 'Забронировать'" for booking
# - "перейди в пункт меню 'Свободные даты'" for availability  
# - "выбери пункт 'Приобрести подарочный сертификат'" for certificates
# - Contact admin: "@the_secret_house"

# CRITICAL: Information Completeness
# Must include specific details from the prompt:
# - Exact room descriptions, amenities, tariff details
# - Precise booking process, payment terms
# - Contact information and links

# CRITICAL: Async Patterns
# All service methods are async, follow existing patterns
async def get_faq_response(self, question: str) -> FAQResponse:
    # Implementation

# CRITICAL: Testing with UV
# Always use uv run pytest for testing
# Test patterns: test_*, async tests supported automatically

# CRITICAL: Current Router Implementation
# FAQ intent already exists but routes to fallback_node
# Need to replace fallback routing with dedicated FAQ node
```

## Implementation Blueprint

### Data models and structure

Create the core FAQ data models for LLM-powered responses and conversation tracking.

```python
# Domain entities for LLM-powered FAQ
@dataclass
class FAQPrompt(BaseModel):
    """LLM prompt configuration for FAQ responses"""
    system_prompt: str  # System context with house information
    temperature: float = 0.7  # Creativity level for responses
    max_tokens: int = 500  # Response length limit
    language: str = "russian"  # Primary response language

@dataclass
class FAQResponse(BaseModel):
    """LLM-generated FAQ response"""
    answer: str  # Generated response from LLM
    tokens_used: int  # Token consumption tracking
    response_time: float  # Response generation time
    needs_human_help: bool = False  # Escalation flag
    suggested_actions: List[str] = []  # Bot function suggestions

@dataclass 
class FAQContext(BaseModel):
    """FAQ conversation context for LLM continuity"""
    conversation_history: List[Dict[str, str]] = []  # [{"role": "user/assistant", "content": "..."}]
    user_preferences: Dict[str, Any] = {}
    session_start: datetime = Field(default_factory=lambda: datetime.now())
    total_questions: int = 0

@dataclass
class HouseInformation(BaseModel):
    """Structured house information for LLM context"""
    location: str
    rooms: Dict[str, str]  # Room name -> description
    amenities: Dict[str, str]  # Amenity -> details  
    tariffs: List[Dict[str, Any]]  # Pricing information
    policies: Dict[str, str]  # Rules and policies
    contact_info: Dict[str, str]  # Contact details
```

### list of tasks to be completed to fullfill the PRP in the order they should be completed

```yaml
Task 1: Create LLM-Powered FAQ Domain Models
CREATE domain/faq/entities.py:
  - IMPLEMENT FAQPrompt, FAQResponse, FAQContext, HouseInformation models
  - USE Pydantic v2 with proper validation and serialization
  - INCLUDE conversation history and token tracking fields
  - FOLLOW patterns from: domain/booking/entities.py

Task 2: Create House Information Context System
CREATE infrastructure/llm/graphs/faq/house_context.py:
  - IMPLEMENT structured house information from user prompt
  - CREATE comprehensive house data: rooms, amenities, tariffs, policies
  - ORGANIZE information for LLM context injection
  - INCLUDE Russian descriptions and specific details

Task 3: Implement LLM-Powered FAQ Service
CREATE application/services/faq_service.py:
  - IMPLEMENT FAQService class with OpenAI LLM integration
  - MIRROR pattern from: infrastructure/llm/extractors/booking_extractor.py for LLM usage
  - ADD conversation context management and prompt engineering
  - INCLUDE the complete house information as system context
  - USE get_llm() from existing OpenAI client

Task 4: Implement FAQ Node
CREATE infrastructure/llm/graphs/faq/faq_node.py:
  - IMPLEMENT faq_node async function
  - FOLLOW pattern from: infrastructure/llm/graphs/available_dates/availability_node.py
  - INTEGRATE with FAQService and pattern matching
  - FORMAT responses with proper tone and Russian language

Task 5: Update App Graph Builder
MODIFY infrastructure/llm/graphs/app/app_graph_builder.py:
  - REPLACE fallback_node with faq_node for FAQ intent
  - UPDATE conditional edges routing
  - PRESERVE existing booking, pricing, availability routing
  - IMPORT faq_node from new module

Task 6: Enhance FAQ Intent Detection
MODIFY infrastructure/llm/graphs/app/router_nodes.py:
  - ENHANCE existing FAQ pattern detection
  - ADD comprehensive Russian question patterns
  - INCLUDE question words: "что", "как", "где", "сколько", "можно ли"
  - PRESERVE existing intent detection logic

Task 7: Add FAQ Configuration
MODIFY core/config.py:
  - ADD FAQ-related settings
  - INCLUDE response templates, confidence thresholds
  - FOLLOW existing Settings class pattern
  - USE environment variable defaults

Task 8: Implement Comprehensive Unit Tests
CREATE tests/unit/domain/faq/test_faq_entities.py:
  - TEST FAQ model validation and serialization
  - TEST Russian text handling and Unicode support
  - FOLLOW pytest patterns from existing tests
  - INCLUDE edge cases and validation scenarios

CREATE tests/unit/application/services/test_faq_service.py:
  - TEST question matching with various patterns
  - TEST response generation with proper tone
  - TEST context tracking and conversation flow
  - MOCK external dependencies, ASYNC test patterns

CREATE tests/unit/infrastructure/llm/graphs/faq/test_faq_node.py:
  - TEST node state handling and response formatting
  - TEST error scenarios and fallback behavior
  - TEST integration with FAQ service
  - INCLUDE Russian language response validation

Task 9: Integration Testing
CREATE tests/integration/test_faq_flow.py:
  - TEST complete FAQ flow from user question to response
  - TEST LangGraph integration and state management
  - TEST various question types and categories
  - INCLUDE conversation context and follow-ups

Task 10: Manual Testing and Polish
MANUAL testing with various question types:
  - House amenities questions
  - Pricing and tariff inquiries
  - Booking process questions
  - Policy and rule questions
  - Edge cases and unknown questions
```

### Per task pseudocode as needed added to each task

```python
# Task 2: House Information Context System
HOUSE_INFORMATION = {
    "location": {
        "address": "12 км от Минска направление агрогородок Ратомка",
        "environment": "в окружении леса, уединённое место без посторонних",
        "security": "закрытая территория участка с автоматическими воротами"
    },
    "rooms": {
        "green_bedroom": "стены зеленого цвета с добавлением дерева, регулиромая подсветка, кастомная кровать 2 на 2.20 метра из советских труб и кресло для фиксации рук и ног Turtur Chair",
        "white_bedroom": "стены белого цвета с добавлением дерева, кастомная деревянная кровать в средневековом стиле с деревянной колодкой, зеркала на стене",
        "secret_room": "специальная мебель и аксессуары для взрослых, андреевский крест, ловушка tarantul, бондажный козел, oral table, подсветка по периметру, зеркальная стена и потолок",
        "kitchen": "холодильник, посудомойка, духовка, плита, вода из фильтра, кофе машина, посуда, различные бокалы, остров в центре",
        "living_room": "тантра кресло, камин, телевизор, качественная музыкальная аппаратура на 300 ват, выход на террасу",
        "sauna": "сухая сауна с электрическим отоплением, пано из можевельника, располагается 4 человека",
        "bathrooms": "на каждом этаже по ванной комнате, на первом душ, на втором ванная, гель, шампунь, кондиционер, полотенца, халаты"
    },
    "tariffs": [
        {
            "name": "ТАРИФ 'СУТОЧНО ОТ 3 ЧЕЛОВЕК'",
            "prices": {"1 день": "700 BYN", "2 дня": "1300 BYN", "3 дня": "1800 BYN"},
            "extras": {"Сауна": "100 BYN", "Фотосессия": "100 BYN"},
            "max_guests": 6,
            "bonus": "При бронировании от 2 дней — дарим 12 часов в подарок при повторном бронировании!"
        }
        # ... other tariffs from user prompt
    ]
}

class HouseContextBuilder:
    def build_system_prompt(self) -> str:
        """Build comprehensive system prompt with house information"""
        return f"""
Ты — виртуальный ассистент The Secret House, уникального загородного дома с современным искусством, стильными интерьерами и специальной «секретной комнатой» в стиле БДСМ.

ИНФОРМАЦИЯ О ДОМЕ:
{self._format_house_info()}

ТВОЯ РОЛЬ:
- Отвечай дружелюбно, уверенно и немного игриво, но всегда уважительно
- Подчёркивай приватность, комфорт и уникальность атмосферы дома
- Используй ТОЛЬКО русский язык для ответов
- При необходимости направляй пользователей к функциям бота

ФУНКЦИИ БОТА:
- Для бронирования: "перейди в пункт меню 'Забронировать'"
- Для свободных дат: "перейди в пункт меню 'Свободные даты'" 
- Для сертификатов: "выбери пункт 'Приобрести подарочный сертификат'"
- Для помощи администратора: "@the_secret_house"
"""

# Task 3: LLM-Powered FAQ Service Implementation
class FAQService:
    def __init__(self):
        self.llm = get_llm()  # Use existing OpenAI client
        self.house_context = HouseContextBuilder()
        self.system_prompt = self.house_context.build_system_prompt()
    
    async def get_faq_response(self, question: str, context: Optional[FAQContext] = None) -> FAQResponse:
        """Generate LLM-powered FAQ response with house context"""
        start_time = time.time()
        
        try:
            # CRITICAL: Build conversation history for context
            conversation_messages = []
            if context and context.conversation_history:
                for msg in context.conversation_history[-6:]:  # Last 6 messages for context
                    conversation_messages.append(msg)
            
            # PATTERN: Create message chain for LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                *[HumanMessage(content=msg["content"]) if msg["role"] == "user" 
                  else AIMessage(content=msg["content"]) for msg in conversation_messages],
                HumanMessage(content=question)
            ]
            
            # CRITICAL: Call LLM with configured parameters
            response = await self.llm.ainvoke(messages)
            answer = response.content
            
            # PATTERN: Extract suggested actions from response
            suggested_actions = self._extract_bot_function_suggestions(answer)
            
            # PATTERN: Track performance metrics
            response_time = time.time() - start_time
            tokens_used = self._estimate_tokens_used(messages, response)
            
            return FAQResponse(
                answer=answer,
                tokens_used=tokens_used,
                response_time=response_time,
                needs_human_help=self._should_escalate_to_human(answer),
                suggested_actions=suggested_actions
            )
            
        except Exception as e:
            logger.exception("Error generating LLM FAQ response")
            # FALLBACK: Return error response
            return FAQResponse(
                answer="Извините, произошла ошибка при обработке вашего вопроса. Обратитесь к администратору @the_secret_house",
                tokens_used=0,
                response_time=time.time() - start_time,
                needs_human_help=True,
                suggested_actions=[]
            )
    
    def _extract_bot_function_suggestions(self, response: str) -> List[str]:
        """Extract bot function suggestions from LLM response"""
        suggestions = []
        if "забронировать" in response.lower():
            suggestions.append("booking")
        if "свободные даты" in response.lower():
            suggestions.append("availability")
        if "сертификат" in response.lower():
            suggestions.append("certificate")
        return suggestions
    
    def _should_escalate_to_human(self, response: str) -> bool:
        """Determine if question should be escalated to human support"""
        escalation_phrases = [
            "не могу ответить",
            "обратитесь к администратору", 
            "свяжитесь с нами",
            "не уверен"
        ]
        return any(phrase in response.lower() for phrase in escalation_phrases)

# Task 4: LLM-Powered FAQ Node Implementation  
async def faq_node(state: AppState) -> Dict[str, Any]:
    """Handle FAQ inquiries with LLM-generated responses"""
    user_text = state.get("text", "")
    user_id = state.get("user_id", 0)
    logger.info("Processing LLM FAQ request", extra={"user_text": user_text, "user_id": user_id})
    
    try:
        # PATTERN: Extract and build FAQ context from conversation history
        faq_context = state.get("faq_context")
        if faq_context:
            faq_context = FAQContext(**faq_context)
        else:
            faq_context = FAQContext()
        
        # CRITICAL: Generate LLM-powered response
        faq_service = FAQService()
        faq_response = await faq_service.get_faq_response(user_text, faq_context)
        
        # PATTERN: Use LLM-generated response directly
        reply = faq_response.answer
        
        # CRITICAL: Add human escalation if needed
        if faq_response.needs_human_help:
            reply += f"\n\n🙋‍♂️ Для получения детальной консультации обращайтесь к администратору @the_secret_house"
        
        # PATTERN: Update conversation context for LLM continuity
        updated_history = faq_context.conversation_history.copy()
        updated_history.append({"role": "user", "content": user_text})
        updated_history.append({"role": "assistant", "content": reply})
        
        new_faq_context = FAQContext(
            conversation_history=updated_history[-12:],  # Keep last 12 messages
            user_preferences=faq_context.user_preferences,
            session_start=faq_context.session_start,
            total_questions=faq_context.total_questions + 1
        )
        
        # PATTERN: Log LLM performance metrics
        logger.info(
            "LLM FAQ response generated",
            extra={
                "user_id": user_id,
                "tokens_used": faq_response.tokens_used,
                "response_time": faq_response.response_time,
                "needs_human_help": faq_response.needs_human_help,
                "suggested_actions": faq_response.suggested_actions
            }
        )
        
        return {
            "reply": reply,
            "faq_data": faq_response.dict(),
            "faq_context": new_faq_context.dict(),
            "intent": "faq"  # Maintain intent
        }
        
    except Exception as e:
        logger.exception(f"Error in faq_node: {e}")
        return {
            "reply": "Произошла ошибка при обработке вашего вопроса. Обратитесь к администратору @the_secret_house для получения помощи.",
            "intent": "faq"
        }

# Task 6: Enhanced Router Pattern Detection
# ENHANCE existing pattern in router_nodes.py
def enhanced_faq_detection(text: str) -> bool:
    """Enhanced FAQ intent detection with comprehensive patterns"""
    faq_patterns = [
        r"(что.*такое|как.*работает|где.*находится|сколько.*стоит)",
        r"(можно ли|нельзя ли|разрешено ли|есть ли)",
        r"(какие.*услуги|что.*входит|что.*включено)",
        r"(правила|условия|политика|требования)",
        r"(как.*добраться|где.*парковка|трансфер)",
        r"(faq|help|info|question|what.*is|how.*does)"
    ]
    
    text_lower = text.lower()
    return any(re.search(pattern, text_lower, re.IGNORECASE | re.UNICODE) for pattern in faq_patterns)
```

### Integration Points

```yaml
GRAPH_ROUTING:
  - modify: infrastructure/llm/graphs/app/app_graph_builder.py
  - pattern: 'g.add_node("faq", faq_node)'
  - pattern: '"faq": "faq"' in conditional_edges mapping
  - change: Remove "faq": "fallback" routing

STATE_MANAGEMENT:
  - uses: infrastructure/llm/graphs/common/graph_state.py
  - pattern: AppState with existing "faq" intent support
  - enhancement: Optional faq_context field for conversation continuity

CONFIG:
  - add to: core/config.py
  - pattern: "FAQ_CONFIDENCE_THRESHOLD = float(os.getenv('FAQ_CONFIDENCE_THRESHOLD', '0.3'))"
  - pattern: "FAQ_MAX_FOLLOWUPS = int(os.getenv('FAQ_MAX_FOLLOWUPS', '2'))"

FALLBACK_ENHANCEMENT:
  - modify: infrastructure/llm/graphs/fallback/fallback_node.py
  - purpose: Handle truly unknown intents that don't match any category
  - pattern: Keep as final fallback for unclassifiable requests
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
# CREATE test_faq_service.py with these test cases:
@pytest.mark.asyncio
async def test_llm_faq_service_amenities_question():
    """Test LLM-powered FAQ response for amenities questions"""
    service = FAQService()
    question = "какие комнаты есть в доме?"
    
    response = await service.get_faq_response(question)
    
    assert isinstance(response.answer, str)
    assert len(response.answer) > 50  # Substantial response
    assert response.tokens_used > 0
    assert response.response_time > 0
    # Check for specific room mentions (LLM should include these from context)
    assert any(room in response.answer.lower() for room in ["спальня", "комната", "сауна"])

@pytest.mark.asyncio  
async def test_llm_faq_service_pricing_question():
    """Test LLM-powered FAQ response for pricing questions"""
    service = FAQService()
    question = "сколько стоит аренда дома?"
    
    response = await service.get_faq_response(question)
    
    assert isinstance(response.answer, str)
    assert response.tokens_used > 0
    # LLM should mention pricing or tariffs
    assert any(price_word in response.answer.lower() for price_word in ["byn", "тариф", "стоимост", "цена"])

@pytest.mark.asyncio
async def test_llm_faq_conversation_context():
    """Test LLM FAQ service with conversation context"""
    service = FAQService()
    
    # First question
    context = FAQContext()
    response1 = await service.get_faq_response("что есть в доме?", context)
    
    # Update context with first response
    context.conversation_history = [
        {"role": "user", "content": "что есть в доме?"},
        {"role": "assistant", "content": response1.answer}
    ]
    
    # Follow-up question
    response2 = await service.get_faq_response("а сколько это стоит?", context)
    
    assert isinstance(response2.answer, str)
    assert response2.tokens_used > 0
    # LLM should handle context and answer about pricing

@pytest.mark.asyncio
async def test_faq_node_conversation_flow():
    """Test FAQ node with conversation context"""
    initial_state = {"text": "что есть в доме?", "user_id": 123}
    
    result = await faq_node(initial_state)
    
    assert "reply" in result
    assert result["intent"] == "faq"
    assert "faq_data" in result
    assert "faq_context" in result

def test_faq_pattern_matching():
    """Test question pattern matching accuracy"""
    matcher = FAQPatternMatcher()
    
    # Test various question types
    test_cases = [
        ("какие комнаты есть?", "amenities"),
        ("сколько стоит аренда?", "pricing"), 
        ("как забронировать?", "booking"),
        ("где находится дом?", "location"),
        ("можно ли курить?", "policies")
    ]
    
    for question, expected_category in test_cases:
        category, confidence = matcher.match_question(question)
        assert category == expected_category
        assert confidence > 0.3

def test_russian_unicode_handling():
    """Test proper Russian text processing"""
    service = FAQService()
    question = "Что такое секретная комната?"  # Mixed case Russian
    
    # Should not raise encoding errors
    response = await service.get_faq_response(question)
    assert isinstance(response.answer, str)
    assert len(response.answer) > 0
```

```bash
# Run and iterate until passing:
uv run pytest tests/unit/ -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test

```bash
# Test the complete FAQ flow through LangGraph
uv run pytest tests/integration/test_faq_flow.py -v

# Manual testing with various question types:
# "что есть в доме?"
# "сколько стоит аренда?"  
# "как забронировать дом?"
# "где находится дом?"
# "можно ли курить?"
# "what amenities are included?"

# Expected responses in Russian with proper tone and information
```

## Final validation Checklist

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check .`
- [ ] No type errors: `uv run mypy .`
- [ ] No format issues: `uv run ruff format . --check`
- [ ] Manual testing successful with various question categories
- [ ] Russian language responses are natural and engaging
- [ ] Proper tone maintained (friendly, confident, slightly playful)
- [ ] Users directed to appropriate bot functions when needed
- [ ] Unknown questions handled gracefully
- [ ] Integration with existing graph flows works correctly
- [ ] FAQ context and conversation continuity working

---

## Anti-Patterns to Avoid

- ❌ Don't provide generic responses - use specific house information
- ❌ Don't use English responses for Russian users - maintain language consistency
- ❌ Don't ignore the specified tone requirements - maintain brand voice
- ❌ Don't fail to direct users to bot functions - missed business opportunities
- ❌ Don't hardcode FAQ responses - use flexible pattern matching
- ❌ Don't ignore conversation context - users expect continuity
- ❌ Don't skip error handling - FAQ system should never crash
- ❌ Don't provide outdated information - ensure accuracy with provided details

## Score Assessment

**Confidence Level: 9.8/10**

This LLM-powered PRP provides exceptional context for one-pass implementation:

- ✅ Complete analysis of existing LangGraph and OpenAI client integration patterns
- ✅ Comprehensive Russian language LLM prompting and tone specifications  
- ✅ Detailed house information structured for LLM system context
- ✅ Clear task breakdown using existing OpenAI client infrastructure
- ✅ Intelligent LLM-based conversation flow with context management
- ✅ Integration with existing bot functions through AI-powered suggestions
- ✅ Comprehensive error handling and graceful LLM fallback strategies
- ✅ Extensive test coverage including LLM response validation
- ✅ Clean Architecture boundaries with proper service layer LLM usage
- ✅ Performance monitoring (tokens, response time) and escalation logic
- ✅ Natural conversation continuity through LLM context windows
- ✅ Business integration through intelligent AI-driven user guidance

**Key LLM Advantages:**
- **Natural Conversations**: ChatGPT provides fluid, contextual responses vs rigid templates
- **Intelligent Routing**: AI can dynamically determine when to suggest bot functions
- **Scalability**: New questions don't require manual pattern updates
- **Tone Consistency**: LLM maintains brand voice through system prompts
- **Context Awareness**: Multi-turn conversations with memory of previous interactions

The implementation should succeed with very high confidence given the existing OpenAI infrastructure, detailed system prompt design, comprehensive house information context, and clear LLM integration patterns. This approach will provide superior user experience with natural, intelligent responses while maintaining business objectives.