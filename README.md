## BingX_api_python-tradingview_to_heroku-by-trader
`2023.01 將tradingview策略的訊號自動發送至bingX交易所`

### requirements
>使用heroku當作雲端站台時所需要的子項目

### trader_example
> 交易員開平倉程式碼範例
* 於交易所創建api後填入
```
    api_key = ""        # put your api_key
    secret_key = ""     # put your secret_key
```
### tradingview_msg_example
>在tradingview alert中訊息欄所放置之訊息，可藉由快訊提取自己所需的部分在程式中使用
```
    data = json.loads(request.data)
```
### 運行
1. 在 command 中輸入 flask run 以在本地端進行測試
2. 測試訊息可使用 tradingview alert 傳出之訊息
3. 使用 insomnia 將訊號 post 至本地端 http://localhost:5000/webhook
4. 確認沒問題即可將程式推上雲端主機完成運行
