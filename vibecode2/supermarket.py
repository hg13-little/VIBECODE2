import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime

# PIL es opcional. Si no está instalado, el programa sigue funcionando.
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# =========================
# DATA MODEL
# =========================

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

daily_earnings = 0.0
current_cart = []
current_customer = ""
customer_done = True
customer_wallet = 0.0
product_images = {}

# Conveyor
belt_running = False
belt_offset = 0
belt_speed = 4
animated_items = []
scanner_x = 580


# =========================
# LOGIC
# =========================

def generate_cart():
    global current_cart

    cart_size = random.randint(2, 5)
    current_cart = random.sample(items, cart_size)

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
    if not PIL_AVAILABLE:
        for item in items:
            product_images[item.name] = None
        return

    for item in items:
        try:
            img = Image.open(item.image_path).resize((40, 40))
            product_images[item.name] = ImageTk.PhotoImage(img)
        except Exception:
            product_images[item.name] = None


def update_display():
    cart_list.delete(*cart_list.get_children())

    total = sum(item.current_price for item in current_cart)
    now = datetime.now().strftime("%H:%M:%S")

    customer_label.config(text=f"Customer: {current_customer}")
    time_label.config(text=f"Time: {now}")
    wallet_label.config(text=f"Customer Cash: ${customer_wallet:.2f}")
    total_label.config(text=f"TOTAL: ${total:.2f}")
    earnings_label.config(text=f"Daily Earnings: ${daily_earnings:.2f}")

    for item in current_cart:
        discount_text = "Yes" if item.current_price < item.base_price else "No"

        # IMPORTANTE:
        # Usamos solo columnas normales en el Treeview.
        # Así evitamos el error TclError: unknown option "$2.0"
        cart_list.insert(
            "",
            "end",
            values=(
                item.name,
                f"${item.current_price:.2f}",
                discount_text
            )
        )


def new_customer():
    global current_customer, customer_done, customer_wallet

    if current_customer and not customer_done:
        return

    customer_done = False
    current_customer = random.choice(customers)

    generate_cart()
    total = sum(item.current_price for item in current_cart)
    customer_wallet = generate_wallet(total)

    result_label.config(text="", foreground="black")
    update_display()


def checkout():
    global daily_earnings, customer_done

    total = sum(item.current_price for item in current_cart)

    if customer_wallet >= total:
        change = round(customer_wallet - total, 2)
        daily_earnings += total
        result_label.config(
            text=f"Payment SUCCESS ✔ | Change: ${change:.2f}",
            foreground="green"
        )
    else:
        shortage = round(total - customer_wallet, 2)
        result_label.config(
            text=f"INSUFFICIENT FUNDS ❌ | Needs ${shortage:.2f}",
            foreground="red"
        )

    customer_done = True
    update_display()


def finish_customer():
    if customer_done:
        new_customer()


def print_receipt():
    receipt = tk.Toplevel(root)
    receipt.title("Receipt")
    receipt.geometry("300x300")

    text = tk.Text(receipt)
    text.pack(fill="both", expand=True)

    total = sum(item.current_price for item in current_cart)

    text.insert("end", "----- RECEIPT -----\n")
    text.insert("end", f"{current_customer}\n")
    text.insert("end", f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    for item in current_cart:
        text.insert("end", f"{item.name} - ${item.current_price:.2f}\n")

    text.insert("end", f"\nTOTAL: ${total:.2f}\n")
    text.insert("end", f"Customer Paid: ${customer_wallet:.2f}\n")

    if customer_wallet >= total:
        text.insert("end", f"Change: ${customer_wallet - total:.2f}\n")
    else:
        text.insert("end", f"Missing: ${total - customer_wallet:.2f}\n")


def clock_out():
    root.destroy()


# =========================
# CONVEYOR
# =========================

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

    # Belt
    conveyor_canvas.create_rectangle(30, 60, 670, 130, fill="#444", outline="")

    # Stripes
    for i in range(-20, 700, 40):
        x1 = i + belt_offset
        conveyor_canvas.create_rectangle(x1, 60, x1 + 20, 130, fill="#666", outline="")

    # Scanner
    conveyor_canvas.create_rectangle(scanner_x, 45, scanner_x + 35, 145, fill="green")
    conveyor_canvas.create_text(scanner_x + 17, 30, text="Scanner")

    # Animated items
    for obj in animated_items:
        x, y = obj["x"], obj["y"]
        conveyor_canvas.create_rectangle(x - 20, y - 20, x + 20, y + 20, fill="white")


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


# =========================
# GUI
# =========================

root = tk.Tk()
root.title("Supermarket Register")
root.geometry("720x650")

customer_label = ttk.Label(root, text="Customer:")
customer_label.pack(pady=4)

time_label = ttk.Label(root, text="Time:")
time_label.pack(pady=4)

wallet_label = ttk.Label(root, text="Customer Cash:")
wallet_label.pack(pady=4)

conveyor_canvas = tk.Canvas(root, width=700, height=180, bg="white")
conveyor_canvas.pack(pady=10)

# Treeview corregido:
# Ya no usamos #0 ni imágenes dentro del insert para evitar el error TclError
cart_list = ttk.Treeview(
    root,
    columns=("Product", "Price", "Discount"),
    show="headings",
    height=8
)

cart_list.heading("Product", text="Product")
cart_list.heading("Price", text="Price")
cart_list.heading("Discount", text="Discount")

cart_list.column("Product", width=220, anchor="center")
cart_list.column("Price", width=100, anchor="center")
cart_list.column("Discount", width=100, anchor="center")

cart_list.pack(pady=10)

total_label = ttk.Label(root, text="TOTAL: $0.00")
total_label.pack(pady=4)

earnings_label = ttk.Label(root, text="Daily Earnings: $0.00")
earnings_label.pack(pady=4)

result_label = ttk.Label(root, text="")
result_label.pack(pady=8)

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

ttk.Button(button_frame, text="Start Belt", command=start_belt).grid(row=0, column=0, padx=5, pady=5)
ttk.Button(button_frame, text="Stop Belt", command=stop_belt).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(button_frame, text="Next Customer", command=new_customer).grid(row=1, column=0, padx=5, pady=5)
ttk.Button(button_frame, text="Checkout", command=checkout).grid(row=1, column=1, padx=5, pady=5)
ttk.Button(button_frame, text="Receipt", command=print_receipt).grid(row=2, column=0, padx=5, pady=5)
ttk.Button(button_frame, text="Finish Customer", command=finish_customer).grid(row=2, column=1, padx=5, pady=5)
ttk.Button(button_frame, text="Clock Out", command=clock_out).grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# START
load_product_images()
setup_conveyor_items()
draw_conveyor()
new_customer()

root.mainloop()
