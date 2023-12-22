from App.App import App
from method1.stock import Stock
import config.config as CONFIG
from method1.order import Order
import pandas as pd 
import time


class Account:

    def __init__(self, app:App, accno:str):
        self.accno = accno
        self.app = app
        self.deposit = self.app.get_deposit() 
        self.account_eval = self.app.get_account_eval()

        self.terminated = False
        self.stocks = {} # {code : stock}  
        
        """ 
            Stock setting
        """

        self.df = pd.read_csv(CONFIG.SETTING_DIR, dtype=CONFIG.SETTING_DTYPE, index_col='code')

        CONFIG.logger.info(f"---------- Stock Info Loading -------------\n\n")
        for code in self.df.index:
            CONFIG.logger.info(f"{code} :")

            state = self.df.loc[code, 'state'].split('|')
            stage = int(state[0]); buy = True if state[1]=='b' else False
            body = list(map(int, self.df.loc[code, 'body'].split('|')))
            stoploss = int(self.df.loc[code, 'stoploss'])
            supRes = list(map(int, self.df.loc[code, 'supRes'].split('|')))
            shareHeld = int(self.df.loc[code, 'quan'])
            assigned_quan = int(self.df.loc[code, 'assigned_quan'])

            self.stocks[code] = Stock(
                app = self.app,
                code = code, 
                supRes = supRes,
                stage = stage,
                buy = buy,
                shareHeld= shareHeld,
                assigned_quan=assigned_quan,
                body=body,
                stoploss = stoploss,
            )

        


    def __str__(self) -> str:
        sb = [str(stock) for stock in self.stocks.values()]
        return '\n'.join(sb)

    def add_order(self, order:Order):

        stock = self.stocks[order.code]
        if order.order_type == CONFIG.BUY:
            stock.buy_orders[order.order_no] = order
            CONFIG.logger.info(f"buy order {order} added.")
        else:
            for d in [3,5,7]:
                if stock.price357[d] == order.price:
                    CONFIG.logger.info(f"f{d} sell order {order} added.")
                    stock.sell_orders[d] = order

    def update_order(self, code:str, ordno:str, remained_quan:int, deal_quan:int, buy:bool):
        self.stocks[code].update_order(ordno = ordno, remained_quan=remained_quan, deal_quan=deal_quan, buy=buy)

    def delete_order(self, code:str, order_no:str, buy:bool):

        
        if buy:
            self.stocks[code].buy_orders.pop(order_no)
        else:
            for spot, order in self.stocks[code].sell_orders.items():
                if order is None: continue
                if order.order_no == order_no:
                    self.stocks[code].sell_orders[spot] = None
        CONFIG.info(f"{code} {'buy' if buy else 'sell'} order({order_no}) deleted.")

    def start(self):
        CONFIG.logger.info(f"\n\n----------------- start ------------------\n\n")
        for stock in self.stocks.values(): stock.start()
        CONFIG.logger.info("account started.")

    def terminate(self):

        self.terminated = True
        for stock in self.stocks.values():
            code = stock.code
            sep = CONFIG.SEP
            self.df.loc[code, "state"] = f"{stock.stage}|{'b' if stock.buy else 's'}"
            self.df.loc[code, "stoploss"] = stock.stoploss
            self.df.loc[code, "body"] = sep.join([str(body) for body in stock.body])
            self.df.loc[code, "supRes"] = sep.join([str(supRes) for supRes in stock.supRes])
            self.df.loc[code, "quan"] = stock.shareHeld
            self.df.loc[code, "assigned_quan"] = stock.assigned_quan
        self.df.to_csv(CONFIG.SETTING_DIR)

    def __del__(self):
        if not self.terminated: self.terminate()

    """
        Monitoring
    """

    def close_buy(self):
        for stock in self.stocks.values():
            if stock.buy==False: continue

            stock.buy=False
            for order in stock.buy_orders.values(): order.cancle()
            if stock.shareHeld== 0: stock.close_position()


    def periodic_bottom_update(self):
        for stock in self.stocks.values():
            stock.check_price()


