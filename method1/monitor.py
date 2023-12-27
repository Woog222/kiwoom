from collections.abc import Callable, Iterable, Mapping
import threading
from typing import Any
from App.App import App
from method1.account import Account
import time, datetime
import config.config as CONFIG
import config.code as CODE
from method1.order import Order
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Monitor(threading.Thread):

    def __init__(self, app:App, account:Account, sleep_time = 2, wait=CONFIG.WAIT):
        super().__init__(daemon=True)
        self.app = app
        self.account = account
        self.running = True
        self.wait = wait
        self.sleep_time = sleep_time
        self.skip=False

        self.noon = False

    def pause(self):
        self.running = False
    
    def resume(self):
        self.running = True
        self.wait=False
        self.skip = True
        self.start()

    def run(self):

            
        if self.wait: 
            CONFIG.logger.info("waiting market to open")
            while not self.app.is_market_open(): time.sleep(1)
            CONFIG.logger.info("market open!")
            self.account.start()
        elif not self.skip:
            self.account.start()    

        """
            Task
        """
        CONFIG.logger.info("monitoring started.")
        while self.running:
           

            """
                market closed?
            """
            if not self.app.is_market_open():
                CONFIG.logger.info(f"market closed. terminate program")
                self.account.terminate()
                self.app.terminate()
                break

            remain=False
            for stock in self.account.stocks.values():
                if not stock.closed: remain=True
            if not remain:
                CONFIG.logger.info(f"all stocks are closed. terminate program")
                self.account.terminate()
                self.app.terminate()
                break
            """
                Price check & order_update
            """    
            codes_to_close = self.account.periodic_bottom_update()
            self.order_update()
            self.account.close_stock(codes=codes_to_close)

            """
                12 check
            """
            if not self.noon and datetime.datetime.now().hour >= 12:
                CONFIG.logger.info("close all buy order at 12:00")
                self.account.close_buy()
                self.noon = True

            """
                get some rest 
            """
            time.sleep(self.sleep_time)

        CONFIG.logger.info("monitor stops.")

    def order_update(self):
        """
        status = self.GetChejanData("913").strip() # "접수" "체결" "확인"
        ret = {}
        ret["order_no"] = self.GetChejanData("9203").strip()
        ret["code"] = self.GetChejanData("9001").strip().strip('A') # "A005930"
        ret["status"] = self.GetChejanData("913").strip() # "접수" or "체결" or "확인"
        ret["order_type"] = self.GetChejanData("905").strip() # "+매수" "매수취소"
        ret["quan"] = int(self.GetChejanData("900").strip())
        ret["remain_quan"] = int(self.GetChejanData("902").strip())
        ret["price"] = int(self.GetChejanData("901").strip())
        ret["origin_order_no"] = self.GetChejanData("904").strip()
        ret["limit"] = self.GetChejanData("906").strip()=="보통" # "보통", "시장가"

        deal_quan = self.GetChejanData("911").strip()
        ret["deal_quan"] = 0 if deal_quan == '' else int(deal_quan)
        """
        while True:
            data = self.app.get_chejan(); 
            if data is None: break
            CONFIG.logger.debug(f"{data} \narrived.")
            # 1. 체결
            if data["status"] == "체결":
                self.account.update_order(code=data["code"], 
                                            ordno=data["order_no"], 
                                            remained_quan=data["remain_quan"], 
                                            deal_quan=data["deal_quan"],
                                            buy= True if data["order_type"]=="+매수" else False)
            # 2. 접수
            elif data["status"] == "접수": # "접수"
                if data["remain_quan"] == 0 or data["order_type"] == "매수취소" or data["order_type"] == "매도취소": # 취소 후 온 더미 주문
                    continue

                order_type = data["order_type"]
                if order_type not in ["-매도", "+매수"]: 
                    CONFIG.logger.info(f"check this order type : {order_type}")
                    continue

                order = Order(app=self.app, 
                            code = data["code"], 
                            order_type= data["order_type"]=="+매수", 
                            order_no= data["order_no"],
                            quantity = data["quan"],
                            price = data["price"])
                self.account.add_order(order=order)

            # 3. 확인 (주로 취소 후)    
            elif data["status"] == "확인":
                order_type = data["order_type"]
                if order_type == "매수취소" or order_type == "매도취소":
                    self.account.delete_order(order_no = data["origin_order_no"], code=data["code"], buy=data["order_type"] == "매수취소")
            else: # another type?
                CONFIG.logger.info(f"{data['status']}arrived")
            
