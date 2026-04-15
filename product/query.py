from fastapi import FastAPI,Path,HTTPException
from db import run_query


from db import run_query


# def init_products():
#     run_query("DELETE FROM products;")

#     run_query(
#         "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s);",
#         ("iPhone", 1000, 5)
#     )

#     run_query(
#         "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s);",
#         ("Laptop", 2000, 3)
#     )



def create_product(name, price, stock, category):
    result=run_query("INSERT INTO products (name,price,stock,category) VALUES(%s,%s,%s,%s) RETURNING id;",(name, price, stock, category), fetch=True)
    return {"message": "Product created","product_id": result[0][0]}


def get_all_products():
    return run_query(
        "SELECT id, name, price, stock, category FROM products;",
        fetch=True
    )


def get_product_by_id(product_id):
    return run_query("SELECT id,name,price,stock,category from products WHERE id =%s ",(product_id,),fetch=True)



def update_stock(product_id,quantity):
    run_query("UPDATE products SET stock= stock -%s WHERE id =%s;",(quantity,product_id,),fetch=True)
    


def reserve_product(product_id, quantity):
    return run_query(
        "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s;",(quantity, product_id, quantity),
        return_rowcount=True
    )


def release_product(product_id, quantity):
    run_query(
        """
        UPDATE products
        SET stock = stock + %s
        WHERE id = %s;
        """,
        ( quantity, product_id)
    )


def search_products_query(query):
    return run_query(
        "SELECT id, name, price, stock, category FROM products WHERE name ILIKE %s OR category ILIKE %s;",
        (f"%{query}%", f"%{query}%"),
        fetch=True
    )


def get_recommendations(category, exclude_ids):
    return run_query(
        "SELECT id, name, price, stock, category FROM products WHERE category = %s AND id NOT IN %s LIMIT 5;",
        (category, tuple(exclude_ids) if exclude_ids else (0,)),
        fetch=True
    )
