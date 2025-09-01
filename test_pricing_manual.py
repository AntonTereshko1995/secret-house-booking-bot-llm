#!/usr/bin/env python3
"""Manual test of pricing functionality"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from domain.booking.pricing import PricingRequest
from application.services.pricing_service import PricingService
from infrastructure.llm.extractors.pricing_extractor import PricingExtractor


async def test_pricing_functionality():
    """Test the complete pricing functionality"""
    print("🧪 Testing pricing functionality...")
    
    try:
        # Test 1: PricingService initialization
        print("\n1. Initializing PricingService...")
        pricing_service = PricingService()
        print(f"   ✓ Loaded {len(pricing_service.tariff_rates)} tariff rates")
        
        # Test 2: Basic pricing calculation
        print("\n2. Testing basic pricing calculation...")
        request = PricingRequest(tariff_id=1, duration_days=1)
        response = await pricing_service.calculate_pricing(request)
        print(f"   ✓ Calculated price: {response.breakdown.total_cost} руб")
        print(f"   ✓ Message: {response.formatted_message[:50]}...")
        
        # Test 3: Multi-day pricing
        print("\n3. Testing multi-day pricing...")
        request = PricingRequest(tariff_id=1, duration_days=2)
        response = await pricing_service.calculate_pricing(request)
        print(f"   ✓ Multi-day price: {response.breakdown.total_cost} руб")
        
        # Test 4: Pricing with add-ons
        print("\n4. Testing pricing with add-ons...")
        request = PricingRequest(tariff_id=0, duration_days=1, add_ons=["sauna", "secret_room"])
        response = await pricing_service.calculate_pricing(request)
        print(f"   ✓ Price with add-ons: {response.breakdown.total_cost} руб")
        print(f"   ✓ Add-ons: {list(response.breakdown.add_on_costs.keys())}")
        
        # Test 5: Natural language extraction
        print("\n5. Testing natural language extraction...")
        extractor = PricingExtractor()
        
        test_queries = [
            "сколько стоит суточный тариф от 3 человек",
            "цена 12-часового тарифа с сауной",
            "стоимость суточного тарифа для двоих на 2 дня"
        ]
        
        for query in test_queries:
            request = await extractor.extract_pricing_requirements(query)
            print(f"   ✓ '{query}' -> tariff: '{request.tariff}', days: {request.duration_days}")
        
        # Test 6: Tariff summary
        print("\n6. Testing tariff summary...")
        summary = await pricing_service.get_tariffs_summary()
        print(f"   ✓ Generated summary ({len(summary)} characters)")
        print(f"   Preview: {summary[:100]}...")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_russian_pricing_queries():
    """Test Russian pricing queries"""
    print("\n🇷🇺 Testing Russian pricing queries...")
    
    extractor = PricingExtractor()
    pricing_service = PricingService()
    
    test_queries = [
        "сколько стоит суточный тариф от 3 человек",
        "цена 12-часового тарифа",
        "стоимость суточного для двоих на 3 дня с сауной",
        "какие у вас цены",
        "тарифы и расценки"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        # Test extraction
        request = await extractor.extract_pricing_requirements(query)
        print(f"  Extracted: tariff='{request.tariff}', days={request.duration_days}, add_ons={request.add_ons}")
        
        # Test pricing calculation if specific tariff found
        if request.tariff or request.tariff_id:
            try:
                response = await pricing_service.calculate_pricing(request)
                print(f"  Price: {response.breakdown.total_cost} руб")
                print(f"  Message preview: {response.formatted_message[:80]}...")
            except Exception as e:
                print(f"  Price calculation failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting pricing functionality tests...\n")
    
    # Run the tests
    success = asyncio.run(test_pricing_functionality())
    
    if success:
        asyncio.run(test_russian_pricing_queries())
    
    print("\n✅ Manual testing complete!")