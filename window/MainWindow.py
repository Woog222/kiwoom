import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import config.config as CONFIG
from Kiwoom.KApp import KApp
from tool.tools import *
from method1.account import Account
from App.App import App
from method1.account import Account
from method1.monitor import Monitor

form_class = uic.loadUiType(CONFIG.WINDOW_UI_DIR)[0]

class MainWindow(QMainWindow, form_class):
    def __init__(self, app:App, account:Account):
        super().__init__()
        
        self.setupUi(self)
        self.app = app
        self.account = account
        self.monitor = Monitor(app=self.app, account=self.account, wait=False)
        self.monitor.start()

        # timer
        self.timer = QTimer(self)
        self.timer.start(3000)

        # handler setting
        self.set_handler()
        



    def set_handler(self):
        self.timer.timeout.connect(self.timeout)
        self.check_button.clicked.connect(self.show_balance)

    """
        Handlers
    """

    def show_interest_stocks(self):
        self.interest_table.setRowCount(len(self.account.stocks))

        for row, stock in enumerate(self.account.stocks.values()):
            name = stock.get_name()

            
            cur_price = self.app.get_current_price(code=stock.get_code())
            buy_price = stock.get_buy_price()
            bottom = stock.get_bottom()
            shareHeld = stock.get_shareHeld()
            assigned_amount = stock.get_assigned_amount()

            for col, data in enumerate(str(stock).split(CONFIG.SEP)):
                try: item = QTableWidgetItem(number_format(data))
                except: item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.interest_table.setItem(row, col, item)
        
        self.interest_table.resizeRowsToContents()

    def show_account_eval(self):
        deposit = self.app.get_deposit()
        df = self.app.get_account_eval()
        
        for col in range(df.shape[1]):
            data = df.iloc[0,col]
            item = QTableWidgetItem(number_format(data))
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.account_table.setItem(0,col+1,item)

        item = QTableWidgetItem(number_format(deposit))
        
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.account_table.setItem(0,0,item)
        self.account_table.resizeRowsToContents()

    def show_stock_eval(self):
        """
        idx -> 종목번호
        ['종목명', '평가손익', '수익률(%)', '보유수량', 
        '매입가', '현재가', '매입금액', '평가금액', '보유비중(%)']
        """

        df = self.app.get_stock_eval()

        row_cnt = df.shape[0]
        self.stock_table.setRowCount(row_cnt)

        for i, idx in enumerate(df.index):
            for j, col in enumerate(CONFIG.STOCK_COLUMNS):
                try:
                    item = QTableWidgetItem(number_format(df.loc[idx, col]))
                except:
                    item = QTableWidgetItem(str(df.loc[idx, col]))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.stock_table.setItem(i, j, item)
        self.stock_table.resizeRowsToContents()
    
    def show_balance(self):
        self.show_account_eval()
        self.show_stock_eval()
        self.show_interest_stocks()

    def timeout(self):
        if self.real_time_button.isChecked():
            self.show_balance()

