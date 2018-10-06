#!/usr/bin/env python
# coding=utf-8
# Author Caner Şen 29.09.2018

import time
import win32api
from client import Client
from config import api_key, api_secret
binance = Client(api_key, api_secret)


Coin='XRP'
symbol=Coin+'BTC'
#CoinSize=2779530283 #For IOTA
CoinSize=39870907279 #For XRP

interval=binance.KLINE_INTERVAL_1MINUTE

import pandas as pd
from stockstats import StockDataFrame as Sdf

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def iota2btc(iota,btc,ratio):
    return (iota-iota,btc+iota*ratio)

def btc2iota(btc,iota,ratio):
    return (btc-int(btc/ratio)*ratio,int(btc/ratio))


def Func_1(symbol):
    result = binance.get_ticker(symbol=symbol)
    return result

def Func_2(symbol):
    result = binance.get_symbol_ticker(symbol=symbol)
    return result

def Func_3(symbol):
    result = binance.get_order_book(symbol=symbol)
    return result    

def Func_4(symbol):
    result = binance.get_all_orders(symbol=symbol)
    return result

def Func_5():
    result = binance.get_account()
    return result
   
def Func_6(symbol):
    result=binance.get_open_orders(symbol=symbol)
    return result

def Func_7(symbol):
    binance.create_test_order(symbol=symbol,side="SELL",type="LIMIT",timeInForce="GTC",quantity=1,price=0.00015600)

def Func_8(symbol,orderId):
    result = binance.cancel_order(symbol=symbol,orderId=orderId)
    return result

def Func_10(symbol,side,quantity,price):
    price=('%.8f' % price)
    binance.order_limit(symbol=symbol, side=side, quantity=quantity, price=price)
    return (price,quantity)

def Func_11(symbol,side,quantity,price):
    price=('%.8f' % price)
    binance.order_limit(symbol=symbol, side=side, quantity=quantity, price=price)
    return None

def updatetime():
    recvWindow=4000
    gt = binance.get_server_time()
    serverTime=gt["serverTime"]
    timestamp=time.time()*1000
    if (timestamp < (serverTime + 1000) and (serverTime - timestamp) <= recvWindow):
        None
    else:
        tt=time.gmtime(int((serverTime)/1000))
        win32api.SetSystemTime(tt[0],tt[1],0,tt[2],tt[3],tt[4],tt[5],0)
    return None

def iota2bnb():
  B=Func_2(symbol="IOTABNB")
  Func_10('IOTABNB','sell',int(1/float(B['price']))+1,float(B['price']))
  return None

def MinAvgMax(symbol):
    h24=Func_1(symbol)
    return (float(h24['lowPrice']),float(h24['weightedAvgPrice']),float(h24['highPrice']))

def average(x):
    sum(x)/len(x)
    return sum(x)/len(x)

def GetPrice(symbol):
    A=Func_1(symbol)
    Price=float(A['lastPrice'])
    #Time=int(A['closeTime'])
    return (Price)

def OpenOrders(symbol):
    value=Func_6(symbol)
    if len(value)!=0:
        orderExist=True
        parite=value[0]['symbol']
        orderId=int(value[0]['orderId'])
        orderorigQty=int(float(value[0]['origQty']))
        orderprice=value[0]['price']
        ordertime=int(value[0]['time'])
        orderexecutedQty=int(float(value[0]['executedQty']))
        side=value[0]['side']        
    if len(value)==0:
        orderExist=False
        parite=''
        orderId=''
        orderorigQty=''
        orderprice=''
        ordertime=''
        orderexecutedQty=''
        side=''
    return (orderExist,parite,orderId,ordertime,side,orderprice,orderorigQty,orderexecutedQty)  


def CheckBalance():
    Account=Func_5()
    Result=[]
    for i in range(len(Account['balances'])):
            if float(Account['balances'][i]['free'])+float(Account['balances'][i]['locked'])>0:
                Result.append(Account['balances'][i])
    return Result    

def DOLAR():
    temp=CheckBalance()
    Total=0
    for i in range(len(temp)):
        asset=temp[i]['asset']
        if asset=='BTC':
            symbol=asset+'USDT'
            GetPrice(symbol)
            Total+=(float(temp[i]['free'])+float(temp[i]['locked']))*GetPrice(symbol)
        else:
            symbol=asset+'BTC'
            GetPrice(symbol)
            Total+=(float(temp[i]['free'])+float(temp[i]['locked']))*GetPrice(symbol)*GetPrice('BTCUSDT')
    return Total       

def CoinBalance(coin):
    init=[]
    temp=CheckBalance()    
    for i in range(len(temp)):
        if coin in temp[i]['asset']:
            init.append(float(temp[i]['free']))
            init.append(float(temp[i]['locked']))
    return init 

def decision(interval,symbol):
    bars=binance.get_klines(symbol=symbol,interval=interval)
    Average=[]  
    Close=[]
    Step=[]
    for i in range(len(bars)):
        Close.append(float(bars[i][4]))
    Average=float(average(Close))
    Step=float(average(Close[400:500]))      
    return (Average,Step)    

def CheckBuyCondition(symbol):
    result=binance.get_my_trades(symbol=symbol)
    if result[len(result)-1]['isBuyer']==False:
        result=binance.get_my_trades(symbol=symbol)  
        x=0
        i=1
        while True:
            if result[len(result)-i]['isBuyer']==False:
                x+=float(result[len(result)-i]['qty'])
                i+=1
            else:
                break        
        fee1=x*0.001*1
        New_coin_qty=int(x+3)
        fee2=New_coin_qty*0.001*1
        btc=CoinBalance('BTC')        
        New_coin_Price=btc[0]/(New_coin_qty+fee2+fee1)        
        return (New_coin_Price,New_coin_qty) 

def timestamp2date(timestamp):
    #gt = binance.get_server_time()
    tt=time.gmtime(int((timestamp)/1000))
    date=str(tt[0]) + '-' + str(tt[1]) + '-' + str(tt[2]) +' ' + str(tt[3]) + ':' +str(tt[4])+':'+str(tt[5])
    return date

def GenerateCSV(interval,symbol,CoinSize):
    bars=binance.get_klines(symbol=symbol,interval=interval)
    Opentime=[]
    Open=[]
    High=[]
    Low=[]
    Close=[]
    Volume=[]
    MarketCap=[]
    string=''
    btcprice=float(GetPrice('BTCUSDT'))
    for i in range(len(bars)):    
        Opentime.append(bars[i][0])
        Open.append(float(bars[i][1])*btcprice)
        High.append(float(bars[i][2])*btcprice)
        Low.append(float(bars[i][3])*btcprice)
        Close.append(float(bars[i][4])*btcprice)
        Volume.append(float(bars[i][5])*btcprice)
        MarketCap.append(float(Open[i])*CoinSize*btcprice)    
    string='Date,Open,High,Low,Close,Volume,Market Cap\n'
    text_file = open("Output.csv", "w")
    text_file.write(string)
    for i in range(len(bars)):
        Date=timestamp2date(Opentime[i])
        string= '"'+Date+'"'+','+'%.8f' % Open[i]+','+'%.8f' % High[i]+','+'%.8f' % Low[i]+','+'%.8f' % Close[i]+','+'"'+'%.8f' % Volume[i]+'"'+','+'"'+'%.8f' % MarketCap[i]+'"'+'\n'
        text_file.write(string)
    text_file.close()
    return (Low[499]/btcprice,High[499]/btcprice)

def Indicator(interval,symbol):
    (Low,High)=GenerateCSV(interval,symbol,CoinSize)
    data   = pd.read_csv('Output.csv')
    stock  = Sdf.retype(data)
    macds = stock['macds']        # Your signal line
    macd   = stock['macd']        # The MACD that need to cross the signal line

    # to give you a Buy/Sell signal
    listLongShort = ["No data"]    # Since you need at least two days in the for loop

    for i in range(1, len(macds)):
        # If the MACD crosses the signal line upward
        if macd[i] > macds[i] and macd[i - 1] <= macds[i - 1]:
            listLongShort.append("BUY")
        # The other way around
        elif macd[i] < macds[i] and macd[i - 1] >= macds[i - 1]:
            listLongShort.append("SELL")
        # Do nothing if not crossed
        else:
            listLongShort.append("HOLD")
            
    stock['Advice'] = listLongShort 
    return(stock,stock['Advice'][499],Low,High) 


#############################################################################
#    END OF FUNCTIONS
#############################################################################


#############################################################################
#    MAIN
#############################################################################

Count=0
Region='-'
Quota=100
btc=CoinBalance('BTC')
bnb=CoinBalance('BNB')
iota=CoinBalance('IOTA')
xrp=CoinBalance('XRP')   
while True:
    try:
        (orderExist,parite,orderId,ordertime,side,orderprice,orderorigQty,orderexecutedQty)=OpenOrders(symbol)                                    
        (stock,Advice,Low,High)=Indicator(interval,symbol)                          
        if Advice =='SELL':
            Region='Decreasing'                
        if Advice =='BUY':
            Region='Increasing'                             
        coin=CoinBalance(Coin)  
        btc=CoinBalance('BTC')
        (Price)=GetPrice(symbol)        
        if orderExist==True:
            time.sleep(0.2)
            print('|Price:','%.8f' % Price,'|B:','%.8f' % btc[0], '|$:','%.2f' % DOLAR(),'|Coin:','%.3f' % coin[0],'|TradeCount:',Count,'|','OrderExist') 
        if orderExist==False:
            if Region=='Decreasing':                        
                if int(coin[0])>0:                                    
                    (Price)=GetPrice(symbol)                
                    (Old_coin_Price,Old_coin_qty)=Func_10(symbol,'sell',int(coin[0]),High) #SELL                                       
                    Count+=1    
                if int(coin[0])==0:
                    (Price)=GetPrice(symbol)            
                    (New_coin_Price,New_coin_qty)=CheckBuyCondition(symbol)                      
                    Func_11(symbol,'buy',New_coin_qty,New_coin_Price) #BUY
                    Count+=1  
            time.sleep(0.2)
            print('|Price:','%.8f' % Price,'|B:','%.8f' % btc[0], '|$:','%.2f' % DOLAR(),'|Coin:','%.3f' % coin[0],'|TradeCount:',Count,'|','Advice=',Advice,'|',Region)
    except:
        print('Hata!')
        updatetime()
        
          