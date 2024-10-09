import sqlite3

# Initialize the database
def initialize_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create a products table
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                      product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      quantity INTEGER NOT NULL,
                      price REAL NOT NULL,
                      category TEXT NOT NULL)''')

    # Create a users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL UNIQUE,
                      password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

initialize_db()

# User Authentication

import bcrypt
import sqlite3

def signup(username, password):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        print("User created successfully.")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    finally:
        conn.close()

def login(username, password):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    record = cursor.fetchone()

    if record and bcrypt.checkpw(password.encode('utf-8'), record[0]):
        print("Login successful!")
        return True
    else:
        print("Invalid username or password.")
        return False


# Inventory managment

def add_product(name, quantity, price, category):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, quantity, price, category) VALUES (?, ?, ?, ?)",
                   (name, quantity, price, category))
    conn.commit()
    conn.close()

def update_product(product_id, name=None, quantity=None, price=None, category=None):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    update_query = "UPDATE products SET "
    update_params = []

    if name:
        update_query += "name = ?, "
        update_params.append(name)
    if quantity:
        update_query += "quantity = ?, "
        update_params.append(quantity)
    if price:
        update_query += "price = ?, "
        update_params.append(price)
    if category:
        update_query += "category = ?, "
        update_params.append(category)

    update_query = update_query.rstrip(', ') + " WHERE product_id = ?"
    update_params.append(product_id)

    cursor.execute(update_query, tuple(update_params))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id=?", (product_id,))
    conn.commit()
    conn.close()

def list_products():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    records = cursor.fetchall()
    for record in records:
        print(record)
    conn.close()


# Report generation

import pandas as pd
import sqlite3

def low_stock_report(threshold=10):
    conn = sqlite3.connect('inventory.db')
    df = pd.read_sql_query("SELECT * FROM products WHERE quantity < ?", conn, params=(threshold,))
    print("Low Stock Products:")
    print(df)
    conn.close()


# GUI using tkinter

import tkinter as tk
from tkinter import messagebox
from inventory import add_product, list_products

def add_product_window():
    def add():
        name = name_entry.get()
        quantity = quantity_entry.get()
        price = price_entry.get()
        category = category_entry.get()

        add_product(name, int(quantity), float(price), category)
        messagebox.showinfo("Success", "Product added successfully")
        window.destroy()

    window = tk.Tk()
    window.title("Add Product")

    tk.Label(window, text="Name").grid(row=0, column=0)
    tk.Label(window, text="Quantity").grid(row=1, column=0)
    tk.Label(window, text="Price").grid(row=2, column=0)
    tk.Label(window, text="Category").grid(row=3, column=0)

    name_entry = tk.Entry(window)
    quantity_entry = tk.Entry(window)
    price_entry = tk.Entry(window)
    category_entry = tk.Entry(window)

    name_entry.grid(row=0, column=1)
    quantity_entry.grid(row=1, column=1)
    price_entry.grid(row=2, column=1)
    category_entry.grid(row=3, column=1)

    tk.Button(window, text="Add", command=add).grid(row=4, column=1)

    window.mainloop()

root = tk.Tk()
tk.Button(root, text="Add Product", command=add_product_window).pack()
root.mainloop()

# Data validation

def validate_product_data(name, quantity, price, category):
    if not name or not category:
        return False, "Name and category are required."
    if quantity <= 0 or price <= 0:
        return False, "Quantity and price must be positive."
    return True, None

# Main program flow

from auth import login
from gui import start_gui

if __name__ == "__main__":
    username = input("Enter username: ")
    password = input("Enter password: ")

    if login(username, password):
        start_gui()  # Start the tkinter GUI


