from App.App import App
import config.config as CONFIG

class Order:

    def __init__(self, app:App, code:str, order_type:int, order_no:str, limit:bool, quantity:int, price:int=0) -> None:
        self.app = app
        self.code = code # stock code
        self.order_type = order_type # CONFIG.BUY OR CONFIG.SELL
        self.order_no = order_no
        self.limit = limit # True or False
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f"{'BUY' if self.order_type==CONFIG.BUY else 'SELL'} ({self.price}, {self.quantity})"

    def cancel(self, quantity:int = -1):
        if quantity < 0 or quantity > self.quantity:
            quantity = self.quantity # cancel all
        
        if self.order_type == CONFIG.BUY:
            self.app.buy_cancle(code=self.code, quantity=quantity, ord_no = self.order_no)
        elif self.order_type == CONFIG.SELL:
            self.app.sell_cancle(code=self.code, quantity=quantity, ord_no = self.order_no )

        

        