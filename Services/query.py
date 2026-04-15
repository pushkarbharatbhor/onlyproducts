from db import run_query
from fastapi import HTTPException
import httpx

PRODUCT_SERVICE_URL = "http://127.0.0.1:9001"


def users():
    return run_query("SELECT * from users;",fetch=True)

# def users(user_id):
#     return run_query("SELECT id,name,balance FROM users WHERE id =%s;",(user_id,),fetch=True)


def orders():
    return run_query("SELECT * FROM orders;",fetch=True)


def create_user(name,balance):
    run_query("INSERT INTO users(name,balance) VALUES(%s,%s);",(name,balance))
    return {"Message":"user created"}



def checking_out(user_id, product_id, quantity):
    #cheking user 
    user=run_query("SELECT id,name,balance FROM users WHERE id=%s;",(user_id,),fetch=True)

    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    user=user[0]


    #get the product 
    product_res=httpx.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
    if product_res.status_code==404:
        raise HTTPException(status_code=404,detail="product not found")
    
    product=product_res.json()

    price=product["price"]
    total_amount=price*quantity

    #3Reserve STock
    reserve_res=httpx.patch(f"{PRODUCT_SERVICE_URL}/products/{product_id}/reserve",params={"quantity":quantity})

    if reserve_res.status_code == 409:
        raise HTTPException(status_code=409, detail="Out of stock")


    #Deduct Balance
    rows_updated=deduct_balance(user_id,total_amount)

    #Relase the product 
    if rows_updated==0:
        httpx.patch(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}/release",params={"quantity":quantity}
        )
        raise HTTPException(status_code=422,detail="Insufficent Balance")
    


    # Create Order 
    order_id=create_order(user_id,total_amount)

    create_order_item(order_id,product_id,quantity,price)

    complete_order(order_id)

    return{
        "message":"order Successful",
        "order_id":order_id
    }




def deduct_balance(user_id,amount):
    return run_query(
        "UPDATE users SET balance=balance- %s WHERE id =%s AND balance >= %s;",(amount,user_id,amount,),return_rowcount=True
    )

def create_order(user_id,total_amount):
    rows=run_query(
        "INSERT INTO orders(user_id,status,total_amount) VALUES (%s,%s,%s) RETURNING id;",(user_id,"Pending",total_amount),fetch=True
    )
    return rows[0][0]

def create_order_item(order_id,product_id,quantity,price):
    run_query("INSERT INTO order_items(order_id,product_id,quantity,price) VALUES(%s,%s,%s,%s);",(order_id,product_id,quantity,price,),return_rowcount=True)

def complete_order(order_id):
    run_query("UPDATE orders SET status=%s WHERE id=%s;",("Cmpleted",order_id,),return_rowcount=True)