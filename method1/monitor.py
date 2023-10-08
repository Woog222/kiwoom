from collections.abc import Callable, Iterable, Mapping
import threading
from typing import Any
from App.App import App
from method1.account import Account
import time
import config.config as CONFIG
import config.code as CODE
from method1.order import Order
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Monitor(QThread):

    stoploss_signal = pyqtSignal(str)

    def __init__(self, app:App, account:Account, sleep_time = 2, wait=True):
        super().__init__()
        self.app = app
        self.account = account
        self.running = True
        self.wait = wait
        self.skip=False

    def pause(self):
        self.running = False
    
    def resume(self):
        self.running = True
        self.wait=False
        self.skip = True
        self.start()

    def run(self):

        if not self.skip and self.wait:
            while not self.app.real_arrived():
                gubun = self.get_real()
                if gubun == CODE.MARKET_OPEN:
                    self.account_start()
                    break
        elif not self.skip:
            self.account.start()    
            print("stated")

        cnt = 0
        while self.running:
            cnt = (cnt + 1)%50

            # real data? (market start_time)
            if self.app.real_arrived():

                gubun =  self.GetCommRealData(code, 215)
                if gubun == CODE.MARKET_CLOSE_SOON:
                    print(gubun, end = " market will be closed soon")

            # price check
            for stock in self.account.stocks.values():
                cur_price = self.app.get_current_price(code= stock.code)
                if cur_price <= stock.get_stoploss():
                    pass

            # chejan check
            while self.app.chejan_arrived():
                data = self.app.get_chejan()

                if data["status"] == "체결":
                    if data["remain_quan"] == 0: 
                        self.account.delete_order(order_no=data["order_no"], code=data["code"])
                    else:
                        self.account.update_order(order_no=data["order_no"], remain_quan = data["remain_quan"])
                elif data["status"] == "접수": # "접수"
                    if data["limit"] == False: continue
                    order = Order(app=self.app, 
                                code = data["code"], 
                                order_type= data["order_type"], 
                                order_no= data["order_no"],
                                limit=data["limit"],
                                quantity = data["quan"],
                                price = data["price"])
                    self.account.add_order(order=order)
                else: # another type?
                    print(data["status"], end="arrived\n")

            # bottom & selling order update        
            if cnt%50 == 0:
                cnt = 1
                self.account.periodic_bottom_update()
                


            time.sleep(2)
