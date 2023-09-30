from collections.abc import Callable, Iterable, Mapping
import threading
from typing import Any
from App.App import App
from method1.account import Account
import time
import config.config as CONFIG
import config.code as CODE
from method1.order import Order


class Monitor(threading.Thread):

    def __init__(self, app:App, account:Account):
        super().__init__(daemon=True)
        self.app = app
        self.account = account



    def run(self):

        cnt = 0

        while True:
            cnt = (cnt + 1)%50
            # real data? (market start_time)
            if self.app.real_arrived():
                gubun = self.get_real()

                if gubun == CODE.MARKET_OPEN:
                    self.account.start()
                elif gubun == CODE.MARKET_CLOSE_SOON:
                    self.ac

            # price check
            self.account.price_check()

            # chejan check
            while True:
                data = self.app.get_chejan()
                if data == False: break

                if data["status"] == "체결":
                    if data["remain_quan"] == 0:
                        self.account.delete_order(order_no=data["order_no"], code=data["code"])
                    else:
                        self.account.update_order(order_no=data["order_no"], remain_quan = data["remain_quan"])
                else: # "접수"
                    if data["limit"] == False: continue
                    order = Order(app=self.app, 
                                code = data["code"], 
                                order_type= data["order_type"], 
                                order_no= data["order_no"],
                                limit=data["limit"],
                                quantity = data["quan"],
                                price = data["price"])
                    self.account.add_order(order=order)

            if cnt%50 == 0:
                self.account.periodic_bottom_update()


            time.sleep(1)
