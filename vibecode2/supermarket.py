import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime
import os
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE=True
except:
    PIL_AVAILABLE=False

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR=os.path.join(BASE_DIR,"images")

class GroceryItem:
    def __init__(self,name,price,image_path):
        self.name=name
        self.base_price=price
        self.current_price=price
        self.image_path=image_path
        self.discount_label=""
        self.discount_amount=0.0
    def reset(self):
        self.current_price=self.base_price
        self.discount_label=""
        self.discount_amount=0.0
    def apple_discount(self):
        self.discount_amount=round(self.base_price*0.5,2)
        self.current_price=round(self.base_price-self.discount_amount,2)
        self.discount_label="2nd unit 50%"
    def chicken_discount(self):
        self.discount_amount=round(self.base_price*0.2,2)
        self.current_price=round(self.base_price-self.discount_amount,2)
        self.discount_label="20% off"

def clone(item):
    x=GroceryItem(item.name,item.base_price,item.image_path)
    return x

items_catalog=[
    GroceryItem("Milk",3.50,os.path.join(IMAGES_DIR,"Milk.png")),
    GroceryItem("Bread",2.00,os.path.join(IMAGES_DIR,"Bread.png")),
    GroceryItem("Eggs",4.00,os.path.join(IMAGES_DIR,"Eggs.png")),
    GroceryItem("Apples",5.00,os.path.join(IMAGES_DIR,"Apples.png")),
    GroceryItem("Chicken",10.00,os.path.join(IMAGES_DIR,"Chicken.png")),
    GroceryItem("Rice",6.00,os.path.join(IMAGES_DIR,"Rice.png"))
]

customers=["Alice","Bob","Charlie","Diana"]

daily_earnings=0.0
customers_served=0
current_cart=[]
scanned_items=[]
current_customer=""
customer_done=True
customer_wallet=0.0
payment_done=False
product_images={}
belt_running=False
belt_offset=0
scanner_x=580
belt_speed=3
belt_objects=[]
scan_flash=0

def generate_cart():
    global current_cart
    current_cart=[]
    for _ in range(random.randint(2,10)):
        item=clone(random.choice(items_catalog))
        item.reset()
        current_cart.append(item)
    apple_count=0
    for item in current_cart:
        if item.name=="Chicken":
            item.chicken_discount()
        elif item.name=="Apples":
            apple_count+=1
            if apple_count%2==0:
                item.apple_discount()

def generate_wallet(total):
    return round(total+random.uniform(-5,20),2)

def scanned_total():
    return round(sum(i.current_price for i in scanned_items),2)

def total_discount():
    return round(sum(i.discount_amount for i in scanned_items),2)

def summary():
    s={}
    for i in scanned_items:
        if i.name not in s:
            s[i.name]={"q":0,"base":0,"disc":0,"final":0,"promo":[]}
        s[i.name]["q"]+=1
        s[i.name]["base"]+=i.base_price
        s[i.name]["disc"]+=i.discount_amount
        s[i.name]["final"]+=i.current_price
        if i.discount_label:
            s[i.name]["promo"].append(i.discount_label)
    return s

def load_images():
    if not PIL_AVAILABLE:
        return
    for i in items_catalog:
        try:
            img=Image.open(i.image_path).resize((48,48))
            product_images[i.name]=ImageTk.PhotoImage(img)
        except:
            product_images[i.name]=None

def update_display():
    cart_list.delete(*cart_list.get_children())
    customers_label.config(text=f"Customers Served: {customers_served}")
    customer_label.config(text=f"Customer: {current_customer}")
    time_label.config(text=f"Time: {datetime.now().strftime('%H:%M:%S')}")
    wallet_label.config(text=f"Cash: ${customer_wallet:.2f}")
    total_label.config(text=f"Total: ${scanned_total():.2f}")
    discount_label.config(text=f"Discount: -${total_discount():.2f}")
    pending_label.config(text=f"Pending: {len(current_cart)-len(scanned_items)}")
    earnings_label.config(text=f"Earnings: ${daily_earnings:.2f}")
    for name,d in summary().items():
        promo=", ".join(set(d["promo"])) if d["promo"] else "-"
        cart_list.insert("", "end", values=(name,d["q"],f"${d['base']:.2f}",promo,f"-${d['disc']:.2f}",f"${d['final']:.2f}"))

def setup_belt():
    global belt_objects
    belt_objects=[]
    for i,x in enumerate(current_cart):
        belt_objects.append({"item":x,"x":80+i*95,"y":95,"scanned":False,"visible":True})

def new_customer():
    global current_customer,customer_done,customer_wallet,scanned_items,payment_done
    if not customer_done:
        return
    scanned_items=[]
    payment_done=False
    current_customer=random.choice(customers)
    customer_done=False
    generate_cart()
    customer_wallet=generate_wallet(sum(i.current_price for i in current_cart))
    setup_belt()
    update_display()
    draw()

def process(o):
    if o["scanned"]:
        return
    o["scanned"]=True
    o["visible"]=False
    scanned_items.append(o["item"])
    update_display()

def checkout():
    global daily_earnings,customer_done,payment_done,customers_served
    if len(scanned_items)<len(current_cart):
        return
    if payment_done:
        return
    total=scanned_total()
    if customer_wallet>=total:
        daily_earnings+=total
    payment_done=True
    customer_done=True
    customers_served+=1
    update_display()

def finish_customer():
    if not customer_done:
        return
    new_customer()

def draw_item(o):
    x,y=o["x"],o["y"]
    img=product_images.get(o["item"].name)
    conveyor.create_rectangle(x-30,y-30,x+30,y+30,fill="white")
    if img:
        conveyor.create_image(x,y,image=img)
    else:
        conveyor.create_text(x,y,text=o["item"].name[:4])

def draw():
    conveyor.delete("all")
    conveyor.create_rectangle(30,60,670,130,fill="#444")
    for i in range(-40,740,40):
        conveyor.create_rectangle(i+belt_offset,60,i+20+belt_offset,130,fill="#666")
    conveyor.create_rectangle(scanner_x,45,scanner_x+35,145,fill="green")
    for o in belt_objects:
        if o["visible"]:
            draw_item(o)

def animate():
    global belt_offset
    if not belt_running:
        draw()
        return
    belt_offset=(belt_offset+3)%40
    for o in belt_objects:
        if o["visible"]:
            o["x"]+=3
            if o["x"]>=scanner_x:
                process(o)
    draw()
    if any(o["visible"] for o in belt_objects):
        root.after(50,animate)

def start_belt():
    global belt_running
    belt_running=True
    animate()

def stop_belt():
    global belt_running
    belt_running=False

def clock_out():
    root.destroy()

root=tk.Tk()
root.geometry("900x750")

customers_label=ttk.Label(root)
customers_label.pack()

customer_label=ttk.Label(root)
customer_label.pack()

time_label=ttk.Label(root)
time_label.pack()

wallet_label=ttk.Label(root)
wallet_label.pack()

conveyor=tk.Canvas(root,width=700,height=180,bg="white")
conveyor.pack()

cart_list=ttk.Treeview(root,columns=("P","Q","B","Promo","D","F"),show="headings")
for c in ("P","Q","B","Promo","D","F"):
    cart_list.heading(c,text=c)
cart_list.pack()

total_label=ttk.Label(root)
total_label.pack()

discount_label=ttk.Label(root)
discount_label.pack()

pending_label=ttk.Label(root)
pending_label.pack()

earnings_label=ttk.Label(root)
earnings_label.pack()

frame=ttk.Frame(root)
frame.pack()

ttk.Button(frame,text="Start Belt",command=start_belt).grid(row=0,column=0)
ttk.Button(frame,text="Stop Belt",command=stop_belt).grid(row=0,column=1)
ttk.Button(frame,text="Next Customer",command=new_customer).grid(row=1,column=0)
ttk.Button(frame,text="Checkout",command=checkout).grid(row=1,column=1)
ttk.Button(frame,text="Finish Customer",command=finish_customer).grid(row=2,column=0)
ttk.Button(frame,text="Clock Out",command=clock_out).grid(row=2,column=1)

load_images()
new_customer()
root.mainloop()
