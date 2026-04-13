import random
from datetime import datetime


#  CLASS 

class GroceryItem:
    __slots__ = ("name", "base_price", "current_price")
    
    def __init__(self, name, price):
        self.name = name
        self.base_price = price
        self.current_price = price
    
    def apply_discount(self, percent):
        if 0 <= percent <= 100:
            discount = self.base_price * (percent / 100)
            self.current_price = round(self.base_price - discount, 2)

    def __str__(self):
        return f"{self.name}: ${self.current_price}"

# STORE DATA

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


# FUNCTIONS

def generate_cart():
    cart = random.sample(items, random.randint(2, 5))
    
    # reset prices
    for item in cart:
        item.current_price = item.base_price

    # apply random sales
    for item in cart:
        if random.random() < 0.3:
            item.apply_discount(20)
    
    return cart

def show_cart(customer, cart):
    print("\n==============================")
    print("Customer:", customer)
    print("Date & Time:", datetime.now())
    print("\nItems:")

    total = 0
    for item in cart:
        print(item)
        total += item.current_price

    print(f"\nTOTAL: ${round(total,2)}")
    print("==============================")

    return total

def print_receipt(customer, cart, payment):
    total = sum(item.current_price for item in cart)

    print("\n🧾 RECEIPT")
    print("-------------------")
    print("Customer:", customer)
    print("Date:", datetime.now())

    for item in cart:
        print(f"{item.name} - ${item.current_price}")

    print("-------------------")
    print(f"TOTAL: ${round(total,2)}")
    print("Payment:", payment)
    print("-------------------")


# MAIN LOOP

while True:
    customer = random.choice(customers)
    cart = generate_cart()

    total = show_cart(customer, cart)

    action = input("\nEnter (c)heckout, (r)eceipt, (n)ext, or (q)uit: ").lower()

    if action == "c":
        payment = input("Payment type (cash/card): ")
        daily_earnings += total
        print("✅ Checkout complete!")

    elif action == "r":
        payment = input("Payment type (cash/card): ")
        print_receipt(customer, cart, payment)

    elif action == "q":
        print("\n⏹️ Clocking out...")
        print(f"Total Earnings: ${round(daily_earnings,2)}")
        break

    print(f"\n💰 Daily Earnings: ${round(daily_earnings,2)}")