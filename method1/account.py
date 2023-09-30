from App.App import App
from method1.stock import Stock
import config.config as CONFIG
from method1.order import Order 


class Account:

    def __init__(self, app:App, accno:str):
        self.accno = accno
        self.app = app
        self.deposit = self.app.get_deposit() 
        self.account_eval = self.app.get_account_eval()

        self.orders = {} # {order_no : order }
        self.stocks = {} # {code : stock}  
        
        """ 
            Stock setting
        """
        with open(CONFIG.SETTING_DIR, 'r') as f:
            code, supRes1, supRes2, supRes3, assigned = f.readline().split()    
            self.stocks[code] = Stock(app=app, code=code, assigned_amount=int(assigned), 
                                      supRes = {1:int(supRes1), 2:int(supRes2), 3:int(supRes3)})
            
            cur_price = self.app.get_current_price(code)
            self.app.price_monitor[code] = {'cur_price' : cur_price, 'min_price':cur_price}
            
        self.app.subscribe(code_list=self.stocks.keys())


    def add_order(self, order:Order):
        self.orders[order.order_no] = order

        stock = self.stocks[order.code]
        if order.order_type == CONFIG.BUY:
            stock.buy_orders[order.order_no] = order
        else:
            stock.sell_orders[order.order_no] = order

    def update_order(self, order_no:str, remain_quan:int):
        self.orders[order_no].quantity = remain_quan

    def delete_order(self, order_no:str, code:str):
        self.orders.pop(order_no)

        stock = self.stocks[code]
        if order_no in stock.buy_orders: stock.buy_orders.pop(order_no)
        if order_no in stock.sell_orders: stock.sell_orders.pop(order_no)


    def start(self):
        for stock in self.stocks.items(): stock.start()
    """
        Monitoring
    """
    def periodic_bottom_update(self):
        for stock in self.stocks.items():
            stock.update_selling_order()

    def price_check(self):
        for stock in self.stocks.values():
            stock.check_price(cur_price = self.app.get_bottom(code = stock.code))




