#coding: utf-8
import urllib.request
import json
import base64
import hmac
import time
from flask import Flask, request

APIURL = "https://api-swap-rest.bingbon.pro"
APIKEY = ""      # your api key
SECRETKEY = ""   # your secret key

def genSignature(path, method, paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr = method + path + paramsStr
    return hmac.new(SECRETKEY.encode("utf-8"), paramsStr.encode("utf-8"), digestmod="sha256").digest()

def post(url, body):
    req = urllib.request.Request(url, data=body.encode("utf-8"), headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req).read()

def getBalance():
    paramsMap = {
        "apiKey": APIKEY,
        "timestamp": int(time.time()*1000),
        "currency": "USDT",
    }
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(genSignature("/api/v1/user/getBalance", "POST", paramsMap)))
    url = "%s/api/v1/user/getBalance" % APIURL
    return post(url, paramsStr)

def getPositions(symbol):
    paramsMap = {
        "symbol": symbol,
        "apiKey": APIKEY,
        "timestamp": int(time.time()*1000),
    }
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(genSignature("/api/v1/user/getPositions", "POST", paramsMap)))
    url = "%s/api/v1/user/getPositions" % APIURL
    return post(url, paramsStr)

def placeOrder(symbol, side, price, volume, tradeType, action):
    paramsMap = {
        "symbol": symbol,
        "apiKey": APIKEY,
        "side": side,
        "entrustPrice": price,
        "entrustVolume": volume,
        "tradeType": tradeType,
        "action": action,
        "timestamp": int(time.time()*1000),
    }
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(genSignature("/api/v1/user/trade", "POST", paramsMap)))
    url = "%s/api/v1/user/trade" % APIURL
    return post(url, paramsStr)

def oneclickclose(symbol,positonId):
    paramsMap = {
        "symbol": symbol,
        "apiKey": APIKEY,
        "positionId": positonId,
        "timestamp": int(time.time()*1000),
    }
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(genSignature("/api/v1/user/oneClickClosePosition", "POST", paramsMap)))
    url = "%s/api/v1/user/oneClickClosePosition" % APIURL
    return post(url, paramsStr)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    action = ''
    data = json.loads(request.data)
    if data['strategy']['order_id'] == 'Long Exit' or data['strategy']['order_id'] == 'close_long':
        side = 'Ask'
        action = 'Close'
    elif data['strategy']['order_id'] == 'Short Exit' or data['strategy']['order_id'] == 'close_short':
        side = 'Bid'
        action = 'Close'    
    elif data['strategy']['order_id'] == 'open_short':
        side = 'Ask'
        action = 'Open'
    elif data['strategy']['order_id'] == 'open_long':
        side = 'Bid'
        action = 'Open'
    elif data['strategy']['order_id'] == 'Close entry(s) order Long Entry' or data['strategy']['order_id'] == 'Close entry(s) order open_long':
        side = 'Ask'
        action = 'Close'
    elif data['strategy']['order_id'] == 'Close entry(s) order Short Entry' or data['strategy']['order_id'] == 'Close entry(s) order open_short':
        side = 'Bid'
        action = 'Close'    

    if data['ticker'] == 'BTCUSDT':
        symbol = 'BTC-USDT'
    elif data['ticker'] == 'ETHUSDT':
        symbol = 'ETH-USDT'   
    elif data['ticker'] == 'BTCUSDT.P':
        symbol = 'BTC-USDT'
    elif data['ticker'] == 'ETHUSDT.P':
        symbol = 'ETH-USDT'   

    openvolume = abs(data['strategy']['position_size'])
    closevolume = abs(data['strategy']['order_contracts'])
    if action == 'Open':
        result = placeOrder(symbol, side, data['strategy']['order_price'], openvolume, "Market", action)
    elif action == 'Close': 
        result = placeOrder(symbol, side, data['strategy']['order_price'], closevolume, "Market", action)         
    elif data['strategy']['order_id'] == 'Long Entry':
        if data['strategy']['order_contracts']*data['strategy']['order_price']>150:
            tracking = getPositions(symbol)
            tracking = json.loads(tracking.decode('utf-8'))
            datalen = len(tracking['data']['positions'])
            for i in range(datalen):
                if tracking['data']['positions'][i]['positionSide'] == 'Short':
                    side = 'Bid'
                    action = 'Close'
                    result = placeOrder(symbol, side, data['strategy']['order_price'], closevolume-openvolume, "Market", action)
                    break
        side = 'Bid'
        action = 'Open'
        result = placeOrder(symbol, side, data['strategy']['order_price'], openvolume, "Market", action)
    elif data['strategy']['order_id'] == 'Short Entry':
        if data['strategy']['order_contracts']*data['strategy']['order_price']>150:
            tracking = getPositions(symbol)
            tracking = json.loads(tracking.decode('utf-8'))
            datalen = len(tracking['data']['positions'])
            for i in range(datalen):
                if tracking['data']['positions'][i]['positionSide'] == 'Long':
                    side = 'Ask'
                    action = 'Close'
                    result = placeOrder(symbol, side, data['strategy']['order_price'], closevolume-openvolume, "Market", action)
                    break
        side = 'Ask'
        action = 'Open'
        result = placeOrder(symbol, side, data['strategy']['order_price'], openvolume, "Market", action)
    tracking = getPositions(symbol)
    tracking = json.loads(tracking.decode('utf-8'))  
    print(tracking)  
    tracking = getBalance()
    tracking = json.loads(tracking.decode('utf-8'))
    print(tracking)
    return {
        'msg':'success'
    }