import pandas as pd

def find_account(accounts:list, acc_no:str):
    if acc_no in accounts:
        return acc_no
    else:
        print(f"{acc_no} is not in {accounts}")
        exit(1)

def change_format(data:str) -> str:
    """
        "00065796" -> "65,796"
    """
    strip_data = data.lstrip('-0')
    if strip_data == '':
        strip_data = '0'

    try:
        format_data = format(int(strip_data), ',d')
    except:
        format_data = format(float(strip_data))

    if data.startswith('-'):
        format_data = '-' + format_data

    return format_data

def number_format(num:int)->str:
    return change_format(str(num))

def divide_three(num:int)->list:
    q = num // 3; r = num % 3
    assert q*3+r == num
    return [q,q,r+q]

def cal_body(open_price:int, last_price:int) -> list:
    """
        previous day open and last_price
    """
    shoulder = int( (open_price + 3*last_price)/4 )
    waist = int( (open_price+ last_price)/2 )
    knee = int( (3*open_price + last_price)/4 )
    return list(map(cal_price, [last_price, open_price, waist, shoulder, knee]))

def tick_size(price:int)->int:

    if   price < 2000  : return 1
    elif price < 5000  : return 5
    elif price < 20000 : return 10
    elif price < 50000 : return 50
    elif price < 200000: return 100
    elif price < 500000: return 500
    else               : return 1000

def round_tick_size(price:int)->int:
    if price<10000:
        if   price < 4000 : return 50
        elif price < 7000 : return 100
        else              : return 200
    elif price <100000:
        if   price < 40000: return 500
        elif price < 70000: return 1000
        else: return 2000
    else: # price<1000000
        if price < 400000 : return 5000
        elif price <700000: return 10000
        else              : return 20000

def cal_price(price:int):
    """
        return the nearest hoga
    """
    tick = tick_size(price)
    r = price % tick
    left = price - r
    right = left + tick
    return left if abs(price-left) <= abs(price-right) else right 

def cal_round_figure(price:int, buy:bool):
    """
    
    """

    # 1. round tick?
    round_tick = round_tick_size(price=price)
    if 7000<=price<10000 or 70000<=price<100000:
        round_tick /= 2

    # 2. cal
    remainder = price%round_tick
    ret = price if remainder == 0 else (price-remainder + round_tick if buy else price-remainder)
    if 7000<=price<10000 or 70000<=price<100000:
        ret += round_tick if buy else (-round_tick)
    
    # 3. buy or sell
    return int(ret + tick_size(ret) if buy else ret)

def cal_avg_price(day_chart:pd.DataFrame, day:int=5):
    """
        only last_price column needed
        default index needed
    """
    ret = 0
    for i in range(day):
        ret += day_chart.loc[i, 'last_price']
    return ret / day


def finding_spots(day_chart:pd.DataFrame, avg_prices:dict, open_price:int,  supRes:dict):
    """
        avg_prices = {5 : 6000, 7 : 5700, 10 : ~, 15 : ~, 20 : ~}
        day_chart columns needed : ['open_price', 'last_price']
    """
    init_value = -1
    ret = {'buy1' : init_value, 'stoploss1': init_value,
           'buy2' : init_value, 'stoploss2': init_value,
           'buy3' : init_value, 'stoploss3': init_value
           }
    
    prev_open_price = day_chart.loc[0,'open_price']
    prev_last_price = day_chart.loc[0,'last_price']
    
    meaninful_spots = cal_body(open_price=prev_open_price, last_price=prev_last_price)

    # method 1
    if prev_last_price < open_price: ret['buy1'] = prev_last_price
    else : 
        avg5 = avg_prices[5]
        for cand in meaninful_spots:
            if avg5 <= cand <= prev_last_price: 
                ret['buy1'] = cand
                break

    ret['stoploss1'] = cal_round_figure(price=avg_prices[5], buy=False)

    # method 2
    for cand in meaninful_spots:
        avg5, avg10  = avg_prices[5], avg_prices[10]
        if avg5 <= cand <= avg10: 
            ret['buy2'] = cand
            break
    if ret['buy2'] == init_value: ret['buy2'] = avg_prices[7]

    ret['stoploss2'] = cal_round_figure(avg_prices[10], buy=False)

    # method 3
    for cand in meaninful_spots:
        avg10, avg20  = avg_prices[10], avg_prices[20]
        if avg10 <= cand <= avg20: 
            ret['buy3'] = cand
            break
    if ret['buy3'] == init_value: ret['buy3'] = avg_prices[15]
    
    ret['stoploss3'] = cal_round_figure(avg_prices[20], buy=False)


    # return 
    return ret


