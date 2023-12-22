from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import config.config as CONFIG
import config.code as CODE
import pythoncom
from App.Kiwoom.KApp import KApp
from window.MainWindow import MainWindow
import datetime, time, sys

from multiprocessing import Process, Manager
from App.App import App
from method1.account import Account
from method1.monitor import Monitor


if __name__ == "__main__":

    app = KApp()
    account = Account(app = app, accno=CONFIG.ACCNO)
    monitor = Monitor(app=app, account=account)


    window_app = QApplication(sys.argv)
    myWindow = MainWindow(app=app, account=account, monitor=monitor)
    myWindow.show()
    window_app.exec_()  








