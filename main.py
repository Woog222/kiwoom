from Kiwoom.KApp import App, MyWindow
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import sys
import win32gui, win32con, win32api

if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # window = MyWindow()
    # window.show()
    # app.exec_()    
    app = App()
    app.buy_stock(code ="005930", quantity=10, limit=False)
    #app.sell_stock(code="005930", quantity=10, limit=False)

