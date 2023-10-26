from abc import *
import pandas as pd

class App(metaclass = ABCMeta):

    """
        order
    """
    @abstractmethod
    def buy(self, code:str, limit:bool, price:int, quantity:int, ord_no:str ="") -> (str, str): pass

    @abstractmethod    
    def buy_cancle(self, code:str, quantity:int, ord_no:str) -> (str, str): pass

    @abstractmethod
    def sell(self, code:str, limit:bool, price:int, quantity:int, ord_no:str = "")-> (str, str): pass

    @abstractmethod
    def sell_cancle(self, code:str, quantity:int, ord_no:str)-> (str, str): pass

    """
        connection
    """

    # @abstractmethod
    # def get_connected(self) -> bool: pass

    """
        account info
    """
    @abstractmethod
    def get_deposit(self) -> int: pass

    @abstractmethod
    def get_stock_eval(self) -> pd.DataFrame: 
        """
            index : 종목번호 
            columns : 종목명 / 평가손익 / 수익률(%) /  보유수량 / 매입가 / 
            현재가 / 매입금액 / 평가금액 / 보유비중(%)
        """
        pass

    @abstractmethod
    def get_account_eval(self)->pd.DataFrame:
        """
        ['총매입금액', '총평가금액', '총평가손익금액', '총수익률(%)', '추정예탁자산']
        """
        
        pass

    """
        info
    """
    @abstractmethod
    def is_market_open(self)-> bool: 
        """
            whether market is available or ,,
        """
        pass
    @abstractmethod
    def is_market_close(self)->bool:
        """
            when your program have to stop
        """
        pass

    @abstractmethod
    def get_chejan(self):
        """
            if received, return chejan data with agreed format
            if not, return None
        """
        pass
    @abstractmethod
    def get_stock_name(self, code:str) -> str:pass

    @abstractmethod
    def get_current_price(self, code:str) -> int: pass

    @abstractmethod
    def get_open_price(self, code:str) -> int:pass

    @abstractmethod
    def get_day_chart(self, code:str, criterion_day, columns:list, size:int) -> pd.DataFrame: pass

    @abstractmethod
    def get_minute_chart(self, code:str, tick_size:int, columns:list, size:int) -> pd.DataFrame: pass

    @abstractmethod
    def subscribe(self, code_list:[str]): 
        """
            price will be updated realtime through price_monitor
        """
        pass

    @abstractmethod
    def unsubscribe(self, code_list:[str]): 
        """
            price won't be updated anymore through price_monitor
        """
        pass


