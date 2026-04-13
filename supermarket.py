import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime


# -----------------------
# DATA MODEL
# -----------------------
class GroceryItem:
    __slots__ = ("name", "base_price", "current_price")

    def __init__(self, name, price):
        self.name = name
        self.base_price = price
        self.current_price = price

    def apply_discount(self, percent):
        discount = self.base_price * (percent / 100)
        self.current_price = round(self.base_price - discount, 2)


items = [
    GroceryItem("Milk", 3.50),
    GroceryItem("Bread", 2.00),
    GroceryItem("Eggs", 4.00),
    GroceryItem("Apples", 5.00),
    GroceryItem("Chicken", 10.00),
    GroceryItem("Rice", 6.00)
]

customers = ["Alice", "Bob", "Charlie", "Diana"]

daily_earnings = 0
current_cart = []
current_customer = ""
customer_done = True  # IMPORTANT FIX


# -----------------------
# LOGIC
# -----------------------
def generate_cart():
    global current_cart

    current_cart = random.sample(items, random.randint(2, 5))

    for item in current_cart:
        item.current_price = item.base_price
        if random.random() < 0.3:
            item.apply_discount(20)


def update_display():
    cart_list.delete(*cart_list.get_children())

    total = 0
    now = datetime.now().strftime("%H:%M:%S")

    customer_label.config(text=f"Customer: {current_customer}")
    time_label.config(text=f"Time: {now}")

    for item in current_cart:
        cart_list.insert("", "end", values=(item.name, f"${item.current_price}"))
        total += item.current_price

    total_label.config(text=f"TOTAL: ${round(total, 2)}")
    earnings_label.config(text=f"Daily Earnings: ${round(daily_earnings, 2)}")


def new_customer():
    global current_customer, customer_done

    # BLOCK switching until current customer is finished
    if current_customer and not customer_done:
        return

    customer_done = False
    current_customer = random.choice(customers)
    generate_cart()
    update_display()


def checkout():
    global daily_earnings, customer_done

    total = sum(item.current_price for item in current_cart)
    daily_earnings += total

    customer_done = True
    update_display()


def finish_customer():
    global customer_done

    # Only allow next customer if current is done
    if customer_done:
        new_customer()


def print_receipt():
    receipt = tk.Toplevel(root)
    receipt.title("Receipt")
    receipt.geometry("300x400")

    text = tk.Text(receipt)
    text.pack(fill="both", expand=True)

    total = sum(item.current_price for item in current_cart)

    text.insert("end", "----- RECEIPT -----\n")
    text.insert("end", f"{current_customer}\n")
    text.insert("end", f"{datetime.now()}\n\n")

    for item in current_cart:
        text.insert("end", f"{item.name} - ${item.current_price}\n")

    text.insert("end", f"\nTOTAL: ${round(total,2)}\n")


def clock_out():
    root.destroy()


# -----------------------
# GUI SETUP
# -----------------------
root = tk.Tk()
root.title("Supermarket Register")
root.geometry("450x520")
root.configure(bg="#f4f4f4")


style = ttk.Style()
style.theme_use("clam")


# Header
header = ttk.Frame(root)
header.pack(pady=10)

customer_label = ttk.Label(header, text="Customer:", font=("Arial", 14))
customer_label.pack()

time_label = ttk.Label(header, text="Time:", font=("Arial", 10))
time_label.pack()


# Cart Table
cart_frame = ttk.Frame(root)
cart_frame.pack(pady=10)

cart_list = ttk.Treeview(cart_frame, columns=("Item", "Price"), show="headings", height=8)
cart_list.heading("Item", text="Item")
cart_list.heading("Price", text="Price")
cart_list.pack()


# Totals
total_label = ttk.Label(root, text="TOTAL: $0", font=("Arial", 14))
total_label.pack(pady=5)

earnings_label = ttk.Label(root, text="Daily Earnings: $0")
earnings_label.pack()


# Payment option
payment_var = tk.StringVar(value="Cash")
ttk.OptionMenu(root, payment_var, "Cash", "Card").pack(pady=5)


# Buttons
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=15)

ttk.Button(btn_frame, text="Next Customer", command=new_customer).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Checkout", command=checkout).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="Receipt", command=print_receipt).grid(row=1, column=0, padx=5)
ttk.Button(btn_frame, text="Finish Customer", command=finish_customer).grid(row=1, column=1, padx=5)
ttk.Button(btn_frame, text="Clock Out", command=clock_out).grid(row=2, column=0, columnspan=2, pady=5)


# Start first customer
new_customer()

root.mainloop()