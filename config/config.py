import os, logging
from datetime import datetime


############# CONFIG ####################

# True  : 08:30 ~ 09:00
# False : market time
WAIT = True # wait for market to open


########################################

# Configure the logging settings
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join("result", f"{datetime.now().time().strftime('%H%M')}.txt"),  # Log file name
    filemode='w'  # Log file mode ('w' for write, 'a' for append)
)

# Create a logger object
logger = logging.getLogger('my_logger')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set the desired logging level
logger.addHandler(console_handler)

SETTING_DTYPE = {
    'code' : str,
    'state' : str,
    'stoploss' : int,
    'body' : str,
    'supRes' : str,
    'quan' : int,
    'assigned_quan' : int,
    'sold' : int,
    'order' : str
}
SEP = '|'

BUY = 1
SELL = 2
BUY_CANCEL = 3
SELL_CANCEL = 4
BUY_AMENDMENT = 5
SELL_AMENDMENT = 6

DAY_TYPE = 1
HOUR_TYPE = 2
MINUTE_TYPE = 3

LIMIT_ORDER = "00"
MARKET_ORDER = "03"


ALLTIME_ACCNO = "8057177211"
DAE_ACCNO = "8057177311"
FUTURE_OPTION_ACCNO = "7016014631"
ACCNO = ALLTIME_ACCNO # target account


CLSID = "KHOPENAPI.KHOpenAPICtrl.1"
STOCK_COLUMNS = ['종목명', '평가손익', '수익률(%)', '보유수량', '매입가',
                   '현재가', '매입금액', '평가금액', '보유비중(%)']
ACCOUNT_COLUMNS =  ["total_purchase_amount", 
                    "total_evaluation_amount", 
                    "total_profit_and_loss_amount", 
                    "total_earnings_rate_percent", 
                    "estimated_deposited_assets"]
CHART_COLUMNS = ['trade_time', 'open_price', 'last_price', 'low_price', 'high_price', 'trading_volume']
CHART_NUM_COLUMNS = ['open_price', 'last_price', 'low_price', 'high_price', 'trading_volume']

"""
    Methods
"""

LOGIN_METHOD = "CommConnect()"



"""
    PATH
"""

WINDOW_UI_DIR = os.path.join("data", "window.ui")
SETTING_DIR = os.path.join("data", "setting.csv")

"""
    MONEY
"""
DEPOSIT_RESERVE = 100000


