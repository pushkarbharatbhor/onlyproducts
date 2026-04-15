from db import run_query

# Add category column if not exists
try:
    run_query("ALTER TABLE products ADD COLUMN category VARCHAR(255);")
    print("Category column added.")
except Exception as e:
    print(f"Column might already exist: {e}")

# Insert some sample products with categories
sample_products = [
    ("Running Shoes", 120.0, 10, "Shoes"),
    ("Basketball Shoes", 150.0, 8, "Shoes"),
    ("Running Socks", 15.0, 20, "Accessories"),
    ("Basketball", 25.0, 15, "Sports"),
    ("Tennis Racket", 80.0, 5, "Sports"),
]

for name, price, stock, category in sample_products:
    try:
        run_query("INSERT INTO products (name, price, stock, category) VALUES (%s, %s, %s, %s);", (name, price, stock, category))
        print(f"Inserted {name}")
    except Exception as e:
        print(f"Product {name} might already exist: {e}")