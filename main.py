from fastapi import FastAPI
from  Services.query import users,orders,checking_out,create_user
from fastapi import FastAPI,HTTPException
from product.query import get_product_by_id,reserve_product,release_product
from product.query import get_all_products,create_product
from product.query import search_products_query, get_recommendations
from chat.query import chat_with_groq
from db import run_query
import uvicorn
import threading

from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int

#Services 
s_app=FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]  # for dev

s_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@s_app.get("/users")
def get_users():
    return users()

@s_app.get("/orders")
def get_orders():
    data = orders()

    return [
        {
            "id": r[0],
            "user_id": r[1],
            "status": r[2],
            "total": float(r[3])
        }
        for r in data
    ]

@s_app.post("/checkout")
def checkout(req: CheckoutRequest):
    return checking_out(req.user_id, req.product_id, req.quantity)

@s_app.post("/new_user")
def new_user(name,balance):
    return create_user(name,balance)



#Products
p_app=FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]  # for dev



p_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    category: str


@p_app.get("/products")
def get_products():
    data = get_all_products()

    return [
        {
            "id": r[0],
            "name": r[1],
            "price": float(r[2]),
            "stock": r[3],
            "category": r[4]
        }
        for r in data
    ]

@p_app.get("/products/{id}")
def get_product_id(id:int):
    data=get_product_by_id(id)

    if not data:
        raise HTTPException(status_code=404,detail="Product not found")
    r=data[0]

    return{
        "id" :r[0],
        "name":r[1],
        "price":float(r[2]),
        "stock":r[3],
        "category":r[4]
    }

@p_app.patch("/products/{product_id}/reserve")
def reserve_pro(product_id:int,quantity:int):
    row_updated=reserve_product(product_id, quantity)
    if row_updated==0:
        raise HTTPException(status_code=409, detail="Out of stock")
    return {"message": "stock reserved"}

@p_app.patch("/products/{product_id}/release")
def release_pro(product_id: int, quantity: int):
    release_product(product_id, quantity)
    return {"message": "stock released"}

@p_app.post("/products")
def create_product_api(req: ProductCreate):
    return create_product(req.name, req.price, req.stock, req.category)



@p_app.get("/search")
def search_products(query: str):
    # Search products by name or category
    search_results = search_products_query(query)
    recommendations = []
    if search_results:
        # Get category of first result
        category = search_results[0][4]
        recommendations = get_recommendations(category, [r[0] for r in search_results])
    return {
        "search_results": [
            {
                "id": r[0],
                "name": r[1],
                "price": float(r[2]),
                "stock": r[3],
                "category": r[4]
            }
            for r in search_results
        ],
        "recommendations": [
            {
                "id": r[0],
                "name": r[1],
                "price": float(r[2]),
                "stock": r[3],
                "category": r[4]
            }
            for r in recommendations
        ]
    }


@p_app.get("/chat")
def chat_product_bot(query: str, user_id: int = None):
    """Chat endpoint using Groq AI with product database context"""
    try:
        result = chat_with_groq(query, user_id)
        return {
            "success": True,
            "query": result["query"],
            "response": result["response"],
            "search_results": result.get("search_results", []),
            "recommendations": result.get("recommendations", []),
            "source": result.get("source"),
            "from_history": result.get("from_history", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@p_app.get("/chat/history")
def get_chat_history(user_id: int = None):
    """Get chat history for a user or all chat history"""
    try:
        if user_id:
            query = "SELECT id, query, response, created_at FROM chat_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 50;"
            history = run_query(query, (user_id,), fetch=True)
        else:
            query = "SELECT id, user_id, query, response, created_at FROM chat_history ORDER BY created_at DESC LIMIT 100;"
            history = run_query(query, fetch=True)
        
        return {
            "success": True,
            "history": [
                {
                    "id": h[0],
                    "user_id": h[1] if user_id is None else user_id,
                    "query": h[2] if user_id is None else h[1],
                    "response": h[3] if user_id is None else h[2],
                    "created_at": str(h[4] if user_id is None else h[3])
                }
                for h in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")



# @p_app.post("/init-data")
# def init_data():
#     return init_products()



def run_services():
    uvicorn.run(s_app, host="127.0.0.1", port=9000)

def run_products():
    uvicorn.run(p_app, host="127.0.0.1", port=9001)

if __name__ == "__main__":
    threading.Thread(target=run_services).start()
    threading.Thread(target=run_products).start()
