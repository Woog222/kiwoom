from Kiwoom.API.kiwoom import Kiwoom
from Kiwoom.kiwoom_impl import *
import config.config as CONFIG
import config.code as CODE
from tool.tools import *
from App.App import App
import time

import multiprocessing as mp
import sys, datetime, os
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import pandas as pd
from Kiwoom.API.proxy import KiwoomProxy





class KApp(App):
    def __init__(self, daemon=True):

        self.accno = CONFIG.ACCNO

        # SubProcess
        # method queue
        self.method_cqueue      = mp.Queue()
        self.method_dqueue      = mp.Queue()

        # tr queue
        self.tr_cqueue          = mp.Queue()
        self.tr_dqueue          = mp.Queue()

        # order queue
        self.order_cqueue       = mp.Queue()
        self.order_dqueue       = mp.Queue()

        # real queue
        self.real_cqueue        = mp.Queue()
        self.real_dqueues       = mp.Queue()

        # condition queue
        self.cond_cqueue        = mp.Queue()
        self.cond_dqueue        = mp.Queue()
        self.tr_cond_dqueue     = mp.Queue()
        self.real_cond_dqueue   = mp.Queue()

        # chejan queue
        self.chejan_dqueue      = mp.Queue()
        self.price_monitor = mp.Manager().dict({}) # {current_price, min_price}

        
        self.proxy = mp.Process(
            target=KiwoomProxy,
            args=(
                # method queue
                self.method_cqueue,
                self.method_dqueue,
                # tr queue
                self.tr_cqueue,
                self.tr_dqueue,
                # order queue
                self.order_cqueue,
                self.order_dqueue,
                # real queue
                self.real_cqueue,
                self.real_dqueues,
                # condition queue
                self.cond_cqueue,
                self.cond_dqueue,
                self.tr_cond_dqueue,
                self.real_cond_dqueue,
                # chejan queue
                self.chejan_dqueue,
                os.getpid(),  # main pid
                self.price_monitor
            ),
            daemon=daemon
        )
        self.proxy.start()

        # 장 시작시간 구독
        self.put_real(cmd = make_real_param(
            subscribe=True, 
            real_type='장시작시간',
            code_list=[],
            fid_list=[],
            screen=CODE.SCR_REAL_MARKET_TIME
        ))



    """ 
        APP
    """
    def buy(self, code: str, limit: bool, price: int, quantity: int, ord_no: str = "") -> (str, str):
        return self.put_order(make_param(order_type=CONFIG.BUY, code=code, accno=self.accno, 
                          quantity=quantity, limit=limit, price=price, order_no=ord_no))
        
        return err_code
            
        
    def sell(self, code: str, limit: bool, price: int, quantity: int, ord_no: str = "") -> (str, str):
        return self.put_order(make_param(kiwoom = self.kiwoom, order_type=CONFIG.BUY, code=code, accno=self.accno, 
                          quantity=quantity, limit=limit, price=price, order_no=ord_no))

        
    def buy_cancle(self, code: str, quantity: int, ord_no: str) -> (str, str):
        return self.put_order(make_param(kiwoom = self.kiwoom, order_type=CONFIG.BUY, code=code, accno=self.accno, 
                          quantity=quantity, limit=True, price=0, order_no=ord_no))

    
    def sell_cancel(self, code: str, quantity: int, ord_no: str) -> (str, str):
        return self.put_order(make_param(kiwoom = self.kiwoom, order_type=CONFIG.BUY, code=code, accno=self.accno, 
                          quantity=quantity, limit=True, price=0, order_no=ord_no))

    
    def get_open_price(self, code:str) -> int:
        self.put_tr(cmd = make_tr_param(
            trcode  = CODE.TR_CURRENT_PRICE,
            rqname  = "cur_price",
            next    = '0',
            screen  = CODE.SCR_TR,
            input   = {'종목코드' : code},
            output  = ['시가']
        ))

        while self.tr_dqueue.empty() : pass
        df, _ = self.get_tr()

        cur_price = df['시가'][0]
        return abs(int(cur_price))
    
    def get_bottom(self, code:str) -> int:
        return self.price_monitor[code]['min_price']
    
    def get_current_price(self, code: str, dynamic=False) -> int:
        if dynamic: return self.price_monitor[code]['current_price']

        self.put_method(('GetMasterLastPrice', code))
        while self.method_dqueue.empty(): pass
        ret = self.get_method()
        return int(ret)

        self.put_tr(cmd = make_tr_param(
            trcode  = CODE.TR_CURRENT_PRICE,
            rqname  = "cur_price",
            next    = '0',
            screen  = CODE.SCR_TR,
            input   = {'종목코드' : code},
            output  = ['현재가']
        ))
        
        while self.tr_dqueue.empty() : pass
        df, _ = self.get_tr()

        cur_price = df['현재가'][0]
        return abs(int(cur_price))

    def get_day_chart(self, code: str, criterion_day = datetime.date.today().strftime("%Y%m%d"),
                      columns = [], size:int=20) -> pd.DataFrame:
        self.put_tr(cmd = make_tr_param(
            trcode  = CODE.TR_DAY_CHART,
            rqname  = f"{code} day chart",
            next    = '0',
            screen  = CODE.SCR_TR,
            input   = {'종목코드' : code, '조회일자' : criterion_day, '수정주가구분' : '1'},
            output  = ['일자', '시가', '현재가', '저가', '고가', '거래량']
        ))
        while self.tr_dqueue.empty() : pass
        df, _ = self.get_tr()

        df = df.head(size)
        df.rename(columns={
            '일자' : 'trade_time',
            '시가' : 'open_price',
            '현재가' : 'last_price',
            '저가': 'low_price',
            '고가': 'high_price',
            '거래량': 'trading_volume'
        }, inplace=True)
        for num_col in CONFIG.CHART_NUM_COLUMNS:
            df[num_col] = df[num_col].astype(int)
            df[num_col] = df[num_col].apply(lambda x : abs(x))
        return df if len(columns)==0 else df[columns]


    def get_minute_chart(self, code:str, tick_size:int = 1, columns:list=[], size:int=20) -> pd.DataFrame:

        self.put_tr(cmd = make_tr_param(
            trcode  = CODE.TR_MINUTE_CHART,
            rqname  = f"{code} MINUTE chart",
            next    = '0',
            screen  = CODE.SCR_TR,
            input   = {'종목코드' : code, '틱범위' : tick_size, '수정주가구분' : '1'},
            output  = ['체결시간', '시가', '현재가', '저가', '고가', '거래량']
        ))
        while self.tr_dqueue.empty() : pass
        df, _ = self.get_tr()


        df = df.head(size)
        df.rename(columns={
            '체결시간' : 'trade_time',
            '시가' : 'open_price',
            '현재가' : 'last_price',
            '저가': 'low_price',
            '고가': 'high_price',
            '거래량': 'trading_volume'
        }, inplace=True)
        for num_col in CONFIG.CHART_NUM_COLUMNS:
            df[num_col] = df[num_col].astype(int)
            df[num_col] = df[num_col].apply(lambda x : abs(x))
        return df if len(columns)==0 else df[columns]
    
    def get_deposit(self) -> int:

        self.put_tr(cmd = make_tr_param(
            trcode = CODE.TR_DEPOSIT,
            rqname = "deposit tr",
            next = '0',
            screen =CODE.SCR_TR,
            input = {"계좌번호" : self.accno},
            output= ['예수금']
        ))
        while self.tr_dqueue.empty() : pass
        df, _ = self.get_tr()
        
        return abs(int(df['예수금'][0]))
    

    def get_stock_eval(self) -> pd.DataFrame:
        """
            종목번호 / 종목명 / 평가손익 / 수익률(%) /  보유수량 / 매입가 / 
            현재가 / 매입금액 / 평가금액 / 보유비중(%)
        """

        ret = []
        cmd = make_tr_param(
            trcode = CODE.TR_ACCOUNT,
            rqname = "account info tr",
            next = '0',
            screen = CODE.SCR_TR,
            input = {"계좌번호" : self.accno},
            output = CONFIG.STOCK_COLUMNS + ['종목번호']
        )
        

        while True:
            self.put_tr(cmd = cmd)
            while self.tr_dqueue.empty(): pass
            df, remained = self.get_tr()
            ret.append(df)

            if remained: cmd['next'] = '2'
            else: break
        
        ret = pd.concat(ret)
        ret.set_index('종목번호', inplace=True)
        ret.sort_values(by='평가금액', inplace=True)

        num_col = ['평가손익', '보유수량', '매입가', '현재가', '매입금액', '평가금액']
        ratio_col = ['수익률(%)', '보유비중(%)']
        ret = ret.astype({col:'int64' for col in num_col})
        for col in num_col:
            if col == '평가손익': continue
            ret[col] = ret[col].apply(lambda x : abs(x))
        ret = ret.astype({col:'float' for col in ratio_col})
        return ret

    


    def get_stock_name(self, code:str) -> str:

        self.put_method(('GetMasterCodeName', code))
        while self.method_dqueue.empty(): pass
        ret = self.get_method()
        return ret

    def get_account_eval(self)->pd.DataFrame:
        korean_cols = ['총매입금액', '총평가금액', '총평가손익금액', '총수익률(%)', '추정예탁자산']

        self.put_tr(cmd = make_tr_param(
            trcode= CODE.TR_ACCOUNT,
            rqname = 'account eval tr',
            next = '0',
            screen = CODE.SCR_TR,
            input = {'계좌번호' : self.accno},
            output = korean_cols
        ))

        while self.tr_dqueue.empty() : pass
        df, _ = self.get_tr()

        df.rename( {
            k:v for k,v in zip(korean_cols, CONFIG.ACCOUNT_COLUMNS)
        })

        for col in ['총매입금액', '총평가금액', '총평가손익금액', '추정예탁자산']:
            df[col] = df[col].astype(int)
        df['total_earin'] = df['총수익률(%)'].astype(float)
        return df
    
    def subscribe(self, code_list:[str]):
        self.put_real(cmd = make_real_param(
            real_type='주식체결',
            subscribe=True,
            code_list=code_list,
            fid_list=['10'],
        ))

    

    """
        tools
    """
    
   
    
    # method
    def put_method(self, cmd):
        self.method_cqueue.put(cmd)

    def get_method(self):
        return self.method_dqueue.get()

    # tr
    def put_tr(self, cmd):
        self.tr_cqueue.put(cmd)

    def get_tr(self):
        return self.tr_dqueue.get()

    # order
    def put_order(self, cmd):
        self.order_cqueue.put(cmd)

    def get_order(self):
        return self.order_dqueue.get()

    # real
    def put_real(self, cmd):
        self.real_cqueue.put(cmd)

    def real_arrived(self):
        return not self.real_dqueues.empty()
    
    def get_real(self):
        return self.real_dqueues.get()

    # condition
    def put_cond(self, cmd):
        self.cond_cqueue.put(cmd)

    def get_cond(self, real=False, method=False):
        if method is True:
            return self.cond_dqueue.get()
        elif real is True:
            return self.real_cond_dqueue.get()
        else:
            return self.tr_cond_dqueue.get()

    def get_chejan(self):
        if self.chejan_dqueue.empty():
            return False
        else:
            return self.chejan_dqueue.get()




