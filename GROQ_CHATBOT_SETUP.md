# AI Chatbot Integration with Groq - Setup Guide

## Overview
Your FastAPI microservice now has an AI-powered chatbot integrated with Groq API that:
- Generates intelligent answers using Groq's Mixtral model
- Searches your product database for relevant products
- Stores and retrieves chat history from the database
- Provides product-aware responses based on your inventory

## ⚠️ IMPORTANT SECURITY WARNING

**Your Groq API key is exposed in the chat/query.py file!**

### Action Required:
1. Visit: https://console.groq.com/keys
2. **Regenerate or delete** the exposed API key: `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`
3. Generate a new API key
4. Update the `GROQ_API_KEY` in `chat/query.py`

### Better Approach (Use Environment Variables):
```python
# In chat/query.py, replace:
GROQ_API_KEY = "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"

# With:
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

Then set the environment variable before running:
```bash
$env:GROQ_API_KEY="your_new_api_key_here"
```

## Installation Steps

### 1. Install Required Python Packages

```bash
pip install groq
```

### 2. Run Database Migration

```bash
python chat_migration.py
```

This creates two new tables:
- `chat_history`: Stores all chat queries and AI responses
- `chat_sessions`: (Optional) For organizing conversations by session

### 3. Restart the Backend

The backend should restart automatically, or run:

```bash
python main.py
```

This starts two services:
- Service API (Port 9000): User and order management
- Product API (Port 9001): Products and Chat

## API Endpoints

### Chat with AI
**Request:**
```
GET /chat?query=Find running shoes&user_id=1
```

**Response:**
```json
{
  "success": true,
  "query": "Find running shoes",
  "response": "I found several great running shoes for you...",
  "search_results": [
    {
      "id": 1,
      "name": "Running Shoes",
      "price": 120.0,
      "stock": 10,
      "category": "Shoes"
    }
  ],
  "recommendations": [...],
  "source": "groq_ai",
  "from_history": false
}
```

### Get Chat History
**Request:**
```
GET /chat/history?user_id=1
```

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "id": 1,
      "user_id": 1,
      "query": "Find running shoes",
      "response": "I found several great running shoes...",
      "created_at": "2024-04-13 10:30:00"
    }
  ]
}
```

## How It Works

### Request Flow:
1. **User asks a question** in the Chat UI
2. **Query is sent to `/chat` endpoint** with optional user_id
3. **Backend checks chat history** for similar cached responses
4. **If no cache hit**: 
   - Search database for matching products
   - Get all products as context
   - Send to Groq AI with system prompt
5. **Groq generates contextual response** based on:
   - Product database context
   - Search results
   - System instructions to keep answers product-focused
6. **Response is saved to database** for future reference
7. **Response displayed to user** in UI with recommendations

### Example Chain:
```
User: "I need shoes for running"
  ↓
Search DB: Finds "Running Shoes" in Shoes category
  ↓
Groq Context: "Available Products: Running Shoes, Basketball Shoes, Tennis Racket..."
  ↓
Groq generates: "Based on your search, I found Running Shoes which are excellent for..."
  ↓
Recommendations: Other products from Shoes category
  ↓
Saved to chat_history table
```

## Frontend Features

### ChatPage.tsx includes:
- **Input field**: Ask product questions
- **Send button**: Submit query to AI
- **AI Response section**: Shows Groq's generated answer
- **Matched Products**: Products the AI found relevant
- **Similar Recommendations**: Related products from same category
- **Chat History sidebar**: View previous queries and responses
  - Click any history item to re-ask it
- **Source indicator**: Shows if response came from cache or AI

## Customization

### Modify AI Behavior

Edit the `system_prompt` in `chat/query.py`:

```python
system_prompt = f"""You are a helpful product recommendation assistant...
# Modify these rules to change AI behavior
1. Only recommend products that exist in the database
2. Always provide product IDs, names, prices, and availability
3. Be friendly, concise, and helpful
...
"""
```

### Change AI Model

In `chat/query.py`, modify:

```python
message = client.chat.completions.create(
    model="mixtral-8x7b-32768",  # Change to: "llama-2-70b-chat", "llama3-70b-8192", etc.
    max_tokens=1024,
    ...
)
```

Available Groq models: Check https://console.groq.com/docs/models

### Cache Configuration

To disable chat history caching:

```python
# In chat/query.py, comment out:
# if history_results and len(history_results) > 0:
#     return cached_response...
```

## Troubleshooting

### "Error generating response: 401"
- API key is invalid or exposed
- Regenerate and update the key in `chat/query.py`

### "Error: groq module not found"
```bash
pip install groq
```

### Chat history not saving
- Run: `python chat_migration.py`
- Check database connection in `db.py`

### Slow responses
- Groq API might be busy
- Try with fewer products in context
- Reduce `max_tokens` from 1024 to 256

## Production Considerations

1. **Security**:
   - Use environment variables for API key
   - Add API rate limiting
   - Validate user_id in requests

2. **Performance**:
   - Add database indexes on `chat_history(user_id, created_at)`
   - Implement pagination for history
   - Cache product list in memory

3. **Monitoring**:
   - Log all chat interactions
   - Monitor Groq API usage
   - Set up error alerts

## Files Modified/Created

```
NEW:
- chat/query.py                 # Groq integration and chat logic
- chat_migration.py             # Database schema

MODIFIED:
- main.py                       # Added /chat endpoint (Groq-enabled) and /chat/history
- enterprise-manager/src/pages/ChatPage.tsx  # Updated UI for AI responses
```

## Next Steps

1. Secure your API key (regenerate it!)
2. Run `python chat_migration.py`
3. Test the chat endpoint with a sample query
4. Customize the system prompt for your use case
5. Deploy to production with environment variables

---

**Questions?** Check the Groq documentation: https://console.groq.com/docs
