from db import run_query
import json
from groq import Groq
import os

# Initialize Groq client
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Use environment variable or fallback to latest available model
# See: https://console.groq.com/docs/models for current available models
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def get_chat_response_from_db(query: str):
    """Fetch similar responses from chat history"""
    return run_query(
        "SELECT response, relevant_products FROM chat_history WHERE LOWER(query) LIKE LOWER(%s) LIMIT 3;",
        (f"%{query}%",),
        fetch=True
    )

def save_chat_history(query: str, response: str, relevant_products: list, user_id: int = None):
    """Save chat query and response to database"""
    products_json = json.dumps(relevant_products)
    run_query(
        "INSERT INTO chat_history (user_id, query, response, relevant_products) VALUES (%s, %s, %s, %s);",
        (user_id, query, response, products_json)
    )

def get_all_products_for_context() -> str:
    """Get all products formatted for AI context"""
    products = run_query(
        "SELECT id, name, price, stock, category FROM products;",
        fetch=True
    )
    
    if not products:
        return "No products available in the database."
    
    product_text = "Available Products:\n"
    for product in products:
        product_text += f"- ID: {product[0]}, Name: {product[1]}, Price: ${product[2]}, Stock: {product[3]}, Category: {product[4]}\n"
    
    return product_text

def generate_ai_response(query: str, product_context: str, search_results: list) -> str:
    """Generate response using Groq AI with product context"""
    
    system_prompt = f"""You are a helpful product recommendation assistant for an e-commerce store. 
Your role is to help customers find products that match their needs.

IMPORTANT RULES:
1. Only recommend products that exist in the database
2. Always provide product IDs, names, prices, and availability
3. If a query is not related to products, politely redirect to product-related topics
4. Be friendly, concise, and helpful
5. Always mention product availability (stock)

{product_context}"""

    search_results_text = ""
    if search_results:
        search_results_text = "\nSearch Results Matching Query:\n"
        for product in search_results:
            search_results_text += f"- {product['name']} (ID: {product['id']}): ${product['price']}, Stock: {product['stock']}, Category: {product['category']}\n"

    user_message = f"{query}{search_results_text}"

    try:
        message = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        return message.choices[0].message.content
    except Exception as e:
        import traceback
        print(f"Groq API Error: {str(e)}")
        print(traceback.format_exc())
        return f"Error: {str(e)}"

def chat_with_groq(query: str, user_id: int = None) -> dict:
    """Main chat function integrating search, AI, and history"""
    
    # First check if this question was asked before
    history_results = get_chat_response_from_db(query)
    if history_results and len(history_results) > 0:
        cached_response = history_results[0][0]
        cached_products = json.loads(history_results[0][1]) if history_results[0][1] else []
        return {
            "query": query,
            "response": cached_response,
            "relevant_products": cached_products,
            "source": "cache",
            "from_history": True
        }
    
    # Search products matching the query
    search_results = run_query(
        "SELECT id, name, price, stock, category FROM products WHERE name ILIKE %s OR category ILIKE %s;",
        (f"%{query}%", f"%{query}%"),
        fetch=True
    )
    
    search_results_formatted = [
        {
            "id": r[0],
            "name": r[1],
            "price": float(r[2]),
            "stock": r[3],
            "category": r[4]
        }
        for r in search_results
    ]
    
    # Get all products context for AI
    product_context = get_all_products_for_context()
    
    # Generate AI response with Groq
    ai_response = generate_ai_response(query, product_context, search_results_formatted)
    
    # Get recommendations from same category
    recommendations = []
    if search_results:
        category = search_results[0][4]
        recs = run_query(
            "SELECT id, name, price, stock, category FROM products WHERE category = %s AND id NOT IN %s LIMIT 5;",
            (category, tuple([r[0] for r in search_results]) if search_results else (0,)),
            fetch=True
        )
        recommendations = [
            {
                "id": r[0],
                "name": r[1],
                "price": float(r[2]),
                "stock": r[3],
                "category": r[4]
            }
            for r in recs
        ]
    
    # Save to chat history
    save_chat_history(query, ai_response, search_results_formatted + recommendations, user_id)
    
    return {
        "query": query,
        "response": ai_response,
        "search_results": search_results_formatted,
        "recommendations": recommendations,
        "source": "groq_ai",
        "from_history": False
    }
