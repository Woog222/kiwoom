from Kiwoom.KApp import KApp
from App.App import App
from tool.tools import *

class Stock:

    def __init__(self, app:App, code:str, assigned_amount:int, supRes:dict, state:int=1) -> None:
        self.app = app
        self.code = code
        self.name = app.get_stock_name(code=code)
        self.assigned_amount = assigned_amount
        self.day_chart = self.app.get_day_chart(code=self.code, columns=['open_price','last_price'], size=20)
        self.supRes = supRes

        self.avg_prices = {}
        for day in [5,7,10,15,20]: self.avg_prices[day] = avg_price(day_chart=self.day_chart, day=day)
        

        """
            real time
        """
        self.state = state
        self.bottom = -1 # start with buy price, updated every minute

        
        self.balance = self.assigned_amount # left money (assigned - buy + sell) (fee need to be included later)

        self.shareHeld = 0
        self.buy_price = -1

        self.buy_orders = {}
        self.sell_orders = {}

        """
            to do
        """
    def __str__(self): 
        """
            state / current_price / bottom / stoploss / assigned_amount  
        """
        sb = [self.state, 
              self.app.get_current_price(code=self.code, dynamic=True), 
              self.bottom,
              self.stop_loss]
        
        return 

    def get_code(self): return self.code
    def get_name(self): return self.name
    def get_buy_price(self): return self.buy_price
    def get_bottom(self): return self.bottom
    def get_shareHeld(self): return self.shareHeld
    def get_assigned_amount(self): return self.assigned_amount

    def update(self):
        # shareHeld
        pass

    """
        To do
    """
    def update_selling_order(self):
        """
            every 1 minute
            3,5,7 update
        """
        # update selling orders
        for order in self.sell_orders:
            order.cancel()

        for d, quantity in zip([3,5,7], divide_three(self.shareHeld)):
            sell_price = cal_price( int(self.botom *(1 + d/100)) )
            self.app.sell(code=self.code, limit=True, price=sell_price, quantity = quantity)

    def close_position(self):
        """
            청산
        """
        # cancel previous selling orders
        for order in self.sell_orders:
            order.cancel()

        self.app.sell(code=self.code, limit=False, quantity = self.shareHeld)
        self.shareHeld = 0

    def start(self):
        # 1. open_price
        self.open_price = self.app.get_open_price(code=self.code)

        # 2. calculating spots (buy, stoploss)
        self.spots = finding_spots(day_chart=self.day_chart, avg_prices=self.avg_prices, open_price=self.open_price, supRes=self.supRes)

        # 3. make buy order
        if self.spots['buy1'] == -1:
            if self.open_price > self.spots['buy2']:
                err_code, self.buy_ord_no = self.app.buy(code=self.code, limit=True, price=self.spots['buy2'], 
                                                         quantity= self.assigned_amount//self.spots['buy2'])
                self.state = 2
            elif self.open_price > self.spots['buy3']:
                err_code, self.buy_ord_no = self.app.buy(code=self.code, limit=True, price=self.spots['buy3'], 
                                                         quantity= self.assigned_amount//self.spots['buy3'])
                self.state = 3
            return
        if self.open_price > self.spots['buy1']:
            err_code, self.buy_ord_no = self.app.buy(code=self.code, limit=True, price=self.spots['buy1'], 
                                                         quantity= self.assigned_amount//self.spots['buy1'])
            self.state = 1
        elif self.open_price > self.spots['buy2']:
            err_code, self.buy_ord_no = self.app.buy(code=self.code, limit=True, price=self.spots['buy2'], 
                                                         quantity= self.assigned_amount//self.spots['buy2'])
            self.state = 2
        elif self.open_price > self.spots['buy3']:
            err_code, self.buy_ord_no = self.app.buy(code=self.code, limit=True, price=self.spots['buy3'], 
                                                         quantity= self.assigned_amount//self.spots['buy3'])
            self.state = 3
            


    """
        just renewing bottom and check stoploss
    """
    def check_price(self, cur_price:int):
        self.bottom = min(self.bottom, cur_price)
        stop_loss = self.spots[f"stop_loss{self.state}"]
        if cur_price <= stop_loss:
            self.close_position()
            """
                todo!!!!!!!!
            """

    