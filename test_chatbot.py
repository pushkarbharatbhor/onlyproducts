#!/usr/bin/env python3
"""Test the full chatbot integration"""

import sys
sys.path.insert(0, 'c:\\Users\\pushkar.bhor\\Desktop\\Practice\\FastAPI\\Project\\microservice')

# Test imports
print("🧪 Testing Chat Module...\n")

try:
    print("1️⃣  Importing chat.query...")
    from chat.query import chat_with_groq
    print("   ✅ Import successful\n")
    
    print("2️⃣  Testing chat_with_groq function...")
    print("   Sending query: 'Find running shoes'\n")
    
    result = chat_with_groq("Find running shoes", user_id=1)
    
    print("3️⃣  Response received!")
    print(f"   Query: {result.get('query')}")
    print(f"   Source: {result.get('source')}")
    print(f"   From History: {result.get('from_history')}")
    print(f"\n   Response Preview:")
    response_text = result.get('response', 'No response')
    if len(response_text) > 200:
        print(f"   {response_text[:200]}...\n")
    else:
        print(f"   {response_text}\n")
    
    print(f"4️⃣  Search Results: {len(result.get('search_results', []))} products found")
    for product in result.get('search_results', [])[:2]:
        print(f"      - {product['name']}: ${product['price']}")
    
    print(f"\n5️⃣  Recommendations: {len(result.get('recommendations', []))} similar products")
    
    print("\n" + "="*60)
    print("🎉 SUCCESS! Chatbot is generating responses!")
    print("="*60)
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("   Make sure chat/query.py exists and db.py is in the same directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
