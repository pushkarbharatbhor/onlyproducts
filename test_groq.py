#!/usr/bin/env python3
"""Test Groq API connection and response"""

from groq import Groq
import os

GROQ_API_KEY = "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"

# Try different models - ordered by likelihood of working
models_to_try = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile", 
    "gemma-7b-it",
    "mixtral-8x7b-32768",
    "llama-3.2-11b-text-preview",
    "llama-3.2-90b-vision-preview",
]

print("🔍 Testing Groq API Connection...\n")

client = Groq(api_key=GROQ_API_KEY)
print("✅ Groq client initialized successfully\n")

MODEL = None
for model in models_to_try:
    try:
        print(f"📤 Trying model: {model}...", end=" ", flush=True)
        message = client.chat.completions.create(
            model=model,
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Hi"}
            ],
            timeout=5
        )
        MODEL = model
        print("✅ WORKS!\n")
        break
    except Exception as e:
        error_msg = str(e).lower()
        if "decommissioned" in error_msg:
            print("❌ Decommissioned")
        elif "404" in error_msg or "not found" in error_msg:
            print("❌ Not found")
        else:
            print(f"❌ {error_msg[:50]}")

if not MODEL:
    print("\n" + "="*60)
    print("⚠️  ISSUE: No working models found!")
    print("="*60)
    print("\nPossible causes:")
    print("1. ❌ Groq API key is invalid/expired")
    print("2. ❌ Account has no quota/credits")
    print("3. ❌ All available models are decommissioned")
    print("\nAction Required:")
    print("1. Visit: https://console.groq.com/keys")
    print("2. Verify your API key is valid")
    print("3. Check remaining quota")
    print("4. Visit: https://console.groq.com/docs/models for available models")
    exit(1)

print("="*60)
print(f"✅ Found working model: {MODEL}")
print("="*60 + "\n")

try:
    # Test basic response
    print("📤 Sending test message...")
    message = client.chat.completions.create(
        model=MODEL,
        max_tokens=256,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Respond briefly."},
            {"role": "user", "content": "Say 'Hello from Groq!' and tell me you're working."}
        ]
    )
    
    response = message.choices[0].message.content
    print(f"✅ Response:\n{response}\n")
    
    # Test with product context
    print("📤 Testing with product context...\n")
    product_context = """Available Products:
- ID: 1, Name: Running Shoes, Price: $120, Stock: 10, Category: Shoes
- ID: 2, Name: Basketball Shoes, Price: $150, Stock: 8, Category: Shoes
- ID: 3, Name: Tennis Racket, Price: $80, Stock: 5, Category: Sports"""
    
    message = client.chat.completions.create(
        model=MODEL,
        max_tokens=256,
        messages=[
            {"role": "system", "content": f"You are a product assistant.\n{product_context}"},
            {"role": "user", "content": "Find running shoes for me"}
        ]
    )
    
    response = message.choices[0].message.content
    print(f"✅ Product Query Response:\n{response}\n")
    print("="*60)
    print("🎉 Groq API is working correctly!")
    print(f"✅ Working model: {MODEL}")
    print("="*60)
    print(f"\n💡 Update chat/query.py with: GROQ_MODEL = \"{MODEL}\"")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
