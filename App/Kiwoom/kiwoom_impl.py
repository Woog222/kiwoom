import config.config as CONFIG
import config.code as CODE


SCREEN_NOS = {
    CONFIG.BUY         : CODE.SCR_BUY,
    CONFIG.SELL        : CODE.SCR_SELL,
    CONFIG.BUY_CANCEL  : CODE.SCR_BUY_CANCEL,
    CONFIG.SELL_CANCEL : CODE.SCR_SELL_CANCEL
}

def make_param(order_type, code:str, accno:str, quantity:int, limit:bool, price:int = 0, order_no:str = ""):
    """
        make order param
    """
    
    return  {
        'rqname' : f"{'limit' if limit else 'market'} price {'buy' if order_type==CONFIG.BUY else 'sell'}",
        'screen' : SCREEN_NOS[order_type],
        'acc_no' : accno,
        'order_type' : order_type,
        'code' : code, 
        'quantity' : quantity,
        'price' : price,
        'hoga_gb' : CONFIG.LIMIT_ORDER if limit else CONFIG.MARKET_ORDER,
        'order_no' : order_no
    }

def make_tr_param(trcode:str, rqname:str, next:str, screen:str, input, output):
    return {
            'trcode' : trcode,
            'rqname' : rqname,
            'next'   : next,
            'screen' : screen,
            'input'  : input,
            'output'  : output
    }

def make_real_param(subscribe:bool, real_type:str, code_list:[str], fid_list:[str], screen:str = CODE.SCR_REAL_PRICE) -> dict:
    return {
        'func_name' : "SetRealReg" if subscribe else "DisConnectRealData",
        'real_type' : real_type,
        "screen"    : screen,
        "code_list" : ';'.join(code_list),
        "fid_list"  : ';'.join(fid_list),
        "opt_type"  : '0'
    }
    