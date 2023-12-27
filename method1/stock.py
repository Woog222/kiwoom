from App.App import App
from tool.tools import *
import config.config as CONFIG
import time

class Stock:

    def __init__(self, app:App, code:str, supRes:[int], stage:int, buy:bool, shareHeld:int, stoploss:int,
                 assigned_quan:int, body:[int], sell_orders:dict = {3:None, 5:None, 7:None}) -> None:
        """
            supRes : descending order list
            shareHeld : holding stock size
        """
        
        """
            const
        """
        self.app = app
        self.code = str(code)
        self.name = str(app.get_stock_name(code=code))

        self.assigned_quan = int(assigned_quan)
        self.day_chart = self.app.get_day_chart(code=self.code, columns=['trade_time','open_price','last_price'], size=30)
        self.supRes = supRes if supRes[0] != -1 else []
        self.body = cal_body(open_price=self.day_chart.loc[0, 'open_price'], last_price = self.day_chart.loc[0,'last_price']) \
            if len(body) < 5 else body 
        
        print(f"\tbody : {self.body}")
        print(f"\tday_chart : \n{self.day_chart.head(5)}\n\n")
        self.avg_prices = {day : cal_avg_price(day_chart=self.day_chart, day=day) for day in [5,7,10,15,20]}
        self.open_price = -1 # at start!
        

        """
            real time
        """
        self.stage = stage
        self.buy = buy
        self.bottom = -1 # start with buy price, updated every minute
        self.price357 = {3:-1, 5:-1, 7:-1}
        if stage == 1: self.stoploss = cal_round_figure(price= self.avg_prices[5], buy=False)
        elif stage == 2: self.stoploss = cal_round_figure(price= self.avg_prices[10], buy=False)
        elif stage == 3: self.stoploss = cal_round_figure(price= self.avg_prices[20], buy=False)
        self.stoploss = max(stoploss, self.stoploss)
        self.shareHeld = shareHeld

        self.buy_orders = {}  # {ordno : Order} after market
        self.sell_orders = {3: None, 5:None, 7:None}
        self.closed=False


    def update_shareHeld(self):
        if self.closed: return
        temp = self.app.get_stock_shareheld(code=self.code)
        if temp != self.shareHeld: 
            CONFIG.info(f"{self.code} shareHeld {self.shareHeld}, but {temp} received.")
        self.shareHeld = temp

    def update_order(self, ordno:str, remained_quan:int, deal_quan:int, buy:bool):
        if self.closed: return
        # REMAINING STOCKS EXIST
        if remained_quan > 0:
            if buy:
                self.shareHeld += deal_quan
                self.update_shareHeld()
                for order_no, order in self.buy_orders.items():
                    if order_no == ordno:
                        log_str = f"buy order updated {str(order)} -> "
                        order.quantity-= deal_quan
                        CONFIG.logger.info(f"{log_str}{str(order)}")
            else: # sell
                self.shareHeld -= deal_quan
                self.update_shareHeld()
                for spot, order in self.sell_orders.items():
                    if order.order_no == ordno:
                        log_str = f"sell order updated {str(order)} -> "
                        order.quantity -= deal_quan
                        CONFIG.logger.info(f"{log_str}{str(order)}")
            return
        
        # close buy order
        if buy:
            self.shareHeld += deal_quan
            self.update_shareHeld()
            
            target_orderno = None
            for order_no, order in self.buy_orders.items():
                if order_no == ordno:
                    CONFIG.logger.info(f"buy order closed {str(order)}.")
                    target_orderno = order_no
            self.buy_orders.pop(target_orderno)
            
            if len(self.buy_orders) == 0:
                self.buy=False
                CONFIG.logger.info(f"buy {target_orderno} order settled. Selling mode on.")
                self.update_bottom(cur_price=self.app.get_current_price(code=self.code))
            return
        else:
            
            # close selling order
            done = False
            self.shareHeld -= deal_quan
            self.update_shareHeld()
            target_orderno = None

            for spot, order in self.sell_orders.items():
                if ordno != self.order.order_no: continue
                done = True 
                target_orderno = order_no
                if spot == 3: 
                    CONFIG.logger.info(f"{self.code} 3% sell order settled.")
                    self.stoploss = self.bottom
                elif spot == 5: 
                    CONFIG.logger.info(f"{self.code} 5% sell order settled.")
                    self.stoploss = self.price357[3]
                else: 
                    CONFIG.logger.info(f"{self.code} 7% sell order settled. this stock will be closed.")
                    self.close_position() # spot 7

                
        


    """
        To do
    """
    def update_bottom(self, cur_price:int):
        """
            every 1 minute
            3,5,7 update
        """
        if self.closed or self.buy or self.bottom <= cur_price: return
        CONFIG.logger.info(f"{self.code} bottom update : {self.bottom} -> {cur_price}")
        self.bottom = cur_price
        for i in [3,5,7]: self.price357[i] = cal_price(int(self.bottom * (1+i/100)))
        
        # update selling orders
        for order in self.sell_orders.values():
            if order is None: continue
            order.cancel()

        for d, quantity in zip([3,5,7], divide_three(self.shareHeld)):
            sell_price = cal_price( int(self.bottom *(1 + d/100)) )
            self.app.sell(code=self.code, limit=True, price=sell_price, quantity = quantity)

    def close_position(self):
        """
            청산
        """
        self.closed = True
        # cancel previous selling orders
        for order in self.buy_orders.values(): 
            if order is not None: order.cancel()
        for order in self.sell_orders.values(): 
            if order is not None: order.cancel()
        self.update_shareHeld()

        if self.shareHeld > 0: self.app.sell(code=self.code, limit=False, quantity = self.shareHeld, price=0)
        CONFIG.logger.info(f"{self.code} closed.\n")
        self.app.unsubscribe(code_list=[self.code])

    def check_fall_through(self):
        """
            acceptable stage transition
        """
        if not self.buy: return

        prev_stage = self.stage
        if self.stage==1:
            if self.avg_prices[10] < self.open_price <= self.avg_prices[5]:
                self.stage = 2
                self.stoploss = cal_round_figure(self.avg_prices[10], buy=False)
            elif self.avg_prices[20] < self.open_price <= self.avg_prices[10]: 
                self.stage=3
                self.stoploss = cal_round_figure(self.avg_prices[20], buy=False)
        elif self.stage==2:
            if self.avg_prices[20] < self.open_price <= self.avg_prices[10]: 
                self.stage=3
                self.stoploss = cal_round_figure(self.avg_prices[20], buy=False)

        if prev_stage != self.stage:
            CONFIG.logger.info(f"{self.code} stage changed : {prev_stage} -> {self.stage}")

    def start(self):
        """
            running!
        """
        # 0. bottom = open_price & 3 5 7 price

        CONFIG.logger.info(f"\n<{self.code} start>\n")

        CONFIG.logger.info(f"waiting for open price..")

        while True:
            temp = self.app.get_open_price(code=self.code) 
            if temp > 0: break
            time.sleep(1)
        self.open_price = self.bottom = temp
        for i in [3,5,7]: self.price357[i] = cal_price(int(self.bottom * (1+0.01*i)))
        CONFIG.logger.info(f"{self.code} open price(bottom) : {self.open_price}")

        # 1.state transition? (1->2,3 / 2->3)
        self.check_fall_through()

        # 2-1. buy
        if self.buy:
            buy_price = int(self.cal_buy_price())
            if buy_price<0: 
                CONFIG.logger.info("buy price < 0, close position")
                self.close_position()
                return
            CONFIG.logger.info(f"gonna buy at {buy_price}")
            self.app.buy(code=self.code, limit=True, price=buy_price, quantity=self.assigned_quan)

        # 2.2 sell
        self.app.subscribe(code_list=[self.code])
            

    def cal_buy_price(self,):
        """
            avg_prices : {5,7,10,15,20 : price}
            last_price : int (prev day)
            open_price : int (today)
            state : 1,2,3
        """
        open_price = self.open_price
        last_price = self.day_chart.loc[0, 'last_price']

        if self.stage==1:
            if open_price > last_price: return last_price
            elif self.avg_prices[5] < open_price <= last_price:
                for cand in self.supRes + self.body:
                    if self.avg_prices[5] < cand <= last_price: 
                        CONFIG.logger.info(f"stage 1, buy_price determined.")
                        return cand
                CONFIG.logger.info(f"buy price")
                return -1
            else:
                # self.close_position()
                return -1
        elif self.stage==2:
            for cand in self.supRes + self.body:
                if self.avg_prices[10] < cand < self.avg_prices[5]: 
                    return cand
            return self.avg_prices[7]
        else: # stage 3    
            for cand in self.supRes + self.body:
                if self.avg_prices[20] < cand < self.avg_prices[10]: 
                    return cand
            return self.avg_prices[15]
    """
        just renewing bottom and check stoploss
    """
    def check_price(self) -> [str]:
        """
            return : [code] if to be closed, or []
        """
        if self.closed: return
        cur_price = self.app.get_current_price(code=self.code)

        if cur_price <= self.stoploss: 
            #CONFIG.logger.info(f"{self.code} price {cur_price} stoploss({self.stoploss}) touched. close position")
            #self.close_position()
            return [self.code]
        self.update_bottom(cur_price=cur_price)
        return []

    def __str__(self): 
        """
            state / current_price / bottom / stoploss / assigned_amount  
        """
        sb = [self.name,
            str(self.stage) + str(self.buy), 
            str(self.app.get_current_price(code=self.code)), 
            str(self.bottom),
            str(self.stoploss),
            str(self.shareHeld) + " now",
            str(self.assigned_quan) + " assigned",
            str(self.body),
            str(self.supRes),
            CONFIG.SEP.join([str(order) for order in self.buy_orders.values()]),
            CONFIG.SEP.join([str(order) for order in self.sell_orders.values()])
        ]
        
        return "  ||  ".join(sb)