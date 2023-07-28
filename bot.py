import json
import websocket
import pprint
import numpy as np
import talib

# SOCKET="wss://ws-feed-public.sandbox.exchange.coinbase.com"
SOCKET="wss://ws-feed.exchange.coinbase.com"

RSI_PERIOD=14
RSI_OVERBOUGHT = 55
RSI_OVERSOLD = 45
TRADE_SYMBOL = "ETH-USD"

closes = []
in_position = False

def on_open(ws):
    print("Websocket connection opened!")
    ws.send(json.dumps({
        "type": "subscribe",
        "product_ids": [TRADE_SYMBOL],
        "channels": ["ticker_batch"]
    }))

def on_close(ws):
    print("Websocket connection closed!")

def on_error(ws, error):
    print("There was an error with the websocket: " + str(error))

def on_message(ws, message):
    global closes, in_position

    print("Received message")
    json_message = json.loads(message)
    pprint.pprint(json_message)
    if json_message["type"] == "ticker":
        closes.append(float(json_message["price"]))
        if len(closes) > RSI_PERIOD:
            np_closes = np.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            current_rsi = rsi[-1]
            print("The current RSI is: " + str(current_rsi))

            if current_rsi > RSI_OVERBOUGHT:
                if not in_position:
                    print("It is overbought, but we just sold, so we don't buy")
                else:
                    print("It is overbought, so we buy!")
                    order_success = buy_order(ws)
                    if order_success:
                        in_position = False
            

            if current_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but we just bought, so we don't sell")
                else:
                    print("It is oversold, so we sell!")
                    order_success = sell_order(ws)
                    if order_success:
                        in_position = True
                

def buy_order(ws):
    return True

def sell_order(ws):
    return True

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
ws.run_forever()