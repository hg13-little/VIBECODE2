import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime
from PIL import Image, ImageTk

# DATA MODEL

class GroceryItem:
    def __init__(self, name, price, image_path):
        self.name = name
        self.base_price = price
        self.current_price = price
        self.image_path = image_path

    def apply_discount(self, percent):
        discount = self.base_price * (percent / 100)
        self.current_price = round(self.base_price - discount, 2)


items = [
    GroceryItem("Milk", 3.50, "images/Milk.png"),
    GroceryItem("Bread", 2.00, "images/Bread.png"),
    GroceryItem("Eggs", 4.00, "images/Eggs.png"),
    GroceryItem("Apples", 5.00, "images/Apples.png"),
    GroceryItem("Chicken", 10.00, "images/Chicken.png"),
    GroceryItem("Rice", 6.00, "images/Rice.png")
]

customers = ["Alice", "Bob", "Charlie", "Diana"]

daily_earnings = 0
current_cart = []
current_customer = ""
customer_done = True
customer_wallet = 0
product_images = {}

# conveyor
belt_running = False
belt_offset = 0
belt_speed = 4
animated_items = []
scanner_x = 580


# LOGIC

def generate_cart():
    global current_cart
    current_cart = random.sample(items, random.randint(2, 5))

    for item in current_cart:
        item.current_price = item.base_price
        if random.random() < 0.3:
            item.apply_discount(20)


def generate_wallet(total_estimate):
    mode = random.random()
    if mode < 0.4:
        return round(total_estimate + random.uniform(0, 10), 2)
    elif mode < 0.8:
        return round(total_estimate * random.uniform(0.7, 1.0), 2)
    else:
        return round(total_estimate + random.uniform(10, 50), 2)


def load_product_images():
    for item in items:
        try:
            img = Image.open(item.image_path).resize((40, 40))
            product_images[item.name] = ImageTk.PhotoImage(img)
        except:
            product_images[item.name] = None  # fallback if image missing


def update_display():
    cart_list.delete(*cart_list.get_children())

    total = sum(item.current_price for item in current_cart)
    now = datetime.now().strftime("%H:%M:%S")

    customer_label.config(text=f"Customer: {current_customer}")
    time_label.config(text=f"Time: {now}")
    wallet_label.config(text=f"Customer Cash: ${customer_wallet}")

    for item in current_cart:
        cart_list.insert(
            "",
            "end",
            text=item.name,
            image=product_images.get(item.name),
            values=(f"${item.current_price}",)
        )

    total_label.config(text=f"TOTAL: ${round(total, 2)}")
    earnings_label.config(text=f"Daily Earnings: ${round(daily_earnings, 2)}")


def new_customer():
    global current_customer, customer_done, customer_wallet

    if current_customer and not customer_done:
        return

    customer_done = False
    current_customer = random.choice(customers)

    generate_cart()
    total = sum(item.current_price for item in current_cart)
    customer_wallet = generate_wallet(total)

    update_display()


def checkout():
    global daily_earnings, customer_done

    total = sum(item.current_price for item in current_cart)

    if customer_wallet >= total:
        change = round(customer_wallet - total, 2)
        daily_earnings += total
        result_label.config(text=f"Payment SUCCESS ✔ | Change: ${change}", foreground="green")
    else:
        shortage = round(total - customer_wallet, 2)
        result_label.config(text=f"INSUFFICIENT FUNDS ❌ | Needs ${shortage}", foreground="red")

    customer_done = True
    update_display()


def finish_customer():
    if customer_done:
        new_customer()


def print_receipt():
    receipt = tk.Toplevel(root)
    receipt.title("Receipt")

    text = tk.Text(receipt)
    text.pack(fill="both", expand=True)

    total = sum(item.current_price for item in current_cart)

    text.insert("end", "----- RECEIPT -----\n")
    text.insert("end", f"{current_customer}\n{datetime.now()}\n\n")

    for item in current_cart:
        text.insert("end", f"{item.name} - ${item.current_price}\n")

    text.insert("end", f"\nTOTAL: ${round(total,2)}\n")
    text.insert("end", f"Customer Paid: ${customer_wallet}\n")


def clock_out():
    root.destroy()


# CONVEYOR

def setup_conveyor_items():
    global animated_items
    animated_items = []

    x_start = 60
    spacing = 95
    y_pos = 95

    for i in range(5):
        animated_items.append({"x": x_start + i * spacing, "y": y_pos})


def draw_conveyor():
    global belt_offset
    conveyor_canvas.delete("all")

    # belt
    conveyor_canvas.create_rectangle(30, 60, 670, 130, fill="#444")

    # stripes
    for i in range(-20, 700, 40):
        x1 = i + belt_offset
        conveyor_canvas.create_rectangle(x1, 60, x1 + 20, 130, fill="#666")

    # scanner
    conveyor_canvas.create_rectangle(scanner_x, 45, scanner_x + 35, 145, fill="green")
    conveyor_canvas.create_text(scanner_x + 17, 30, text="Scanner")

    # items
    for obj in animated_items:
        x, y = obj["x"], obj["y"]
        conveyor_canvas.create_rectangle(x-20, y-20, x+20, y+20, fill="white")


def animate_conveyor():
    global belt_offset

    if belt_running:
        belt_offset = (belt_offset + belt_speed) % 40

        for obj in animated_items:
            obj["x"] += 2
            if obj["x"] > scanner_x:
                obj["x"] = 60

        draw_conveyor()
        root.after(50, animate_conveyor)
    else:
        draw_conveyor()


def start_belt():
    global belt_running
    if not belt_running:
        belt_running = True
        animate_conveyor()


def stop_belt():
    global belt_running
    belt_running = False


# GUI

root = tk.Tk()
root.title("Supermarket Register")
root.geometry("600x600")

customer_label = ttk.Label(root, text="Customer:")
customer_label.pack()

time_label = ttk.Label(root, text="Time:")
time_label.pack()

wallet_label = ttk.Label(root, text="Customer Cash:")
wallet_label.pack()

conveyor_canvas = tk.Canvas(root, width=700, height=180, bg="white")
conveyor_canvas.pack()

cart_list = ttk.Treeview(root, columns=("Price",), show="tree headings", height=8)
cart_list.heading("#0", text="Product")
cart_list.heading("Price", text="Price")
cart_list.pack()

total_label = ttk.Label(root, text="TOTAL: $0")
total_label.pack()

earnings_label = ttk.Label(root, text="Daily Earnings: $0")
earnings_label.pack()

result_label = ttk.Label(root, text="")
result_label.pack()

# buttons
ttk.Button(root, text="Start Belt", command=start_belt).pack()
ttk.Button(root, text="Stop Belt", command=stop_belt).pack()

ttk.Button(root, text="Next Customer", command=new_customer).pack()
ttk.Button(root, text="Checkout", command=checkout).pack()
ttk.Button(root, text="Receipt", command=print_receipt).pack()
ttk.Button(root, text="Finish Customer", command=finish_customer).pack()
ttk.Button(root, text="Clock Out", command=clock_out).pack()


# START
load_product_images()
setup_conveyor_items()
draw_conveyor()
new_customer()

root.mainloop()
