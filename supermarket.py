import random 

class GroceryItem:
    __slots__ = ("name", "base_price", "current_price")
    
    def __init__(self, name, price,):
        self.name = name
        self.base_price = price
        self.current_price = price
    
    def apply_discount(self, percent):
        if 0 <= percent <= 100
