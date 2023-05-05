import threading
from twilio.rest import Client
from pprint import pprint
import pandas as pd
from fyers_api import fyersModel, accessToken
import os
import time
from fyers_api.Websocket import ws
import pdb
# from datetime import datetime
import datetime

app_id = "X93SP59B62-100"
app_secret = "0LJ1I6XFTE"
redirect_url = "https://www.google.com/"


def access_token_generator():
    if not os.path.exists("AccessToken.txt"):
        session = accessToken.SessionModel(client_id=app_id,
                                           secret_key=app_secret, redirect_uri=redirect_url,
                                           response_type="code", grant_type="authorization_code")
        response = session.generate_authcode()

        print(response)
        auth_code = input("Enter Auth Code:")
        session.set_token(auth_code)
        access_token = session.generate_token()["access_token"]
        with open("AccessToken.txt", "w") as f:
            f.write(access_token)

    else:
        with open("AccessToken.txt", "r") as f:
            access_token = f.read()

    return access_token


# ----------------- CONTROL PARAMETERS ---------------------

TARGET_LTP = 10
LIMIT_PRICE_TOLERANCE = 0.5
global Latest_Order_book  # This is the copy of the most resent orderbook with order status - This value must update after every order requrest to the exchange or after a break in connection
global order_position  # This gives the positions for the day
symbol_one = "MCX:NATURALGAS23MAYFUT"  # The 1st instrument being traded by this API

INSTRUMENT_symbol = "MCX:NATURALGAS23MAYFUT"  # for testing only
INSTRUMENT_LTP = 230  # for testing only

# Only for testing
# INSTRUMENT_LTP = 16

fyers = fyersModel.FyersModel(client_id=app_id, token=access_token_generator(), log_path='')

# pprint(fyers.get_profile())

ws_access_token = f"{app_id}:{access_token_generator()}"

data_type = "symbolData"
run_background = False

symbol = ["MCX:NATURALGAS23MAYFUT","MCX:NATURALGAS23JUNFUT"]
symbol_list = ["MCX:NATURALGAS23MAYFUT","MCX:NATURALGAS23JUNFUT"]
live_data = {}


# SYMBOL MASTER SHEET TO SPREADSHEETS

# link = 'https://public.fyers.in/sym_details/NSE_FO.csv'
#
#
# headers_name = ["Fytoken", "Symbol Details", "Exchange Instrument type", "Minimum lot size", "Ticket size", "ISIN",
#                 "Trading Session", "Last update date", "Expiry date", "Symbol ticker", "Exchange", "Segment",
#                 "Scrip code", "Name", "Underlying scrip code", "Strike Price", "Option type"]
#
# pd.read_csv(link, names = headers_name).to_csv("NSE_FO.csv")


# data = {"symbol": "NSE:IOC-EQ"}
# print(fyers.quotes(data))


def custom_message(msg):
    # print(f"Custom:{msg}")
    # pprint(msg)
    # pdb.set_trace()

    for symbol in msg:
        live_data[symbol['symbol']] = symbol['ltp']
        # pdb.set_trace()


    target_instrument = live_data['MCX:NATURALGAS23MAYFUT']


"""# CODE FOR HISTORICAL DATA

data = {"symbol":"NSE:SBIN-EQ","resolution":"60","date_format":"0","range_from":"1622097600","range_to":"1622097685","cont_flag":"1"}
print(fyers.history(data))
"""

""" # REQUESTING QUOTES FOR INSTRUMENTS

data = {"symbols":"NSE:SBIN-EQ,NSE:ACC-EQ"}
for i in fyers.quotes(data)["d"]:
    print(i)
"""

fyersSocket = ws.FyersSocket(access_token=ws_access_token, run_background=False, log_path="")
fyersSocket.websocket_data = custom_message


def subscribe_new_symbol(symbol_list):
    global fyersSocket, data_type
    fyersSocket.subscribe(symbol=symbol_list, data_type=data_type)
    # fyersSocket.subscribe(data_type="orderUpdate")


threading.Thread(target=subscribe_new_symbol, args=(symbol,)).start()

# print("TA_Python")

""" QUOTE Method

data = {"symbol": "NSE:SBIN-EQ", "resolution": "60", "date_format": "1", "range_from": "2023-02-01",
            "range_to": "2023-02-03", "cont_flag": "1"}

#print(fyers.funds())
#print(fyers.holdings())


data3 = {"symbols":"NSE:NIFTY-INDEX"}

# data_nfo = {"symbols":"NSE:NIFTY2320917900CE"}

data_nfo = [{"symbols":"NSE:SBIN-EQ"},
            {"symbols":"NSE:CIPLA23FEB1000PE"},
            {"symbols":"NSE:IDEA-EQ"}]

# pprint(fyers.holdings())
# pprint(fyers.quotes(data_nfo))
quote = fyers.quotes(data_nfo)
new_list = []
for i in data_nfo:
    new_dict= {i["symbols"]: fyers.quotes(i)['d'][0]['v']['lp']}
    # pprint(fyers.quotes(i))
    new_list.append(new_dict)
pprint(new_list)

CIPLA1000PE_LTP = new_list[1]['NSE:CIPLA23FEB1000PE']
IDEA_LTP = new_list[2]['NSE:IDEA-EQ']


if IDEA_LTP>7:
    print("yes")
pdb.set_trace()

"""



# pdb.set_trace()


# Time_Extractor - converting orderdatetime to seconds from market open


# def RECENT_ORDER():
#     for orderBook in Latest_Order_book['orderBook']:
#         order_time = datetime.datetime.strptime(orderBook['orderDateTime'], '%d-%b-%Y %H:%M:%S')
#         order_time_sec = Time_Extractor(order_time)
#         current_time = datetime.datetime.now()
#         current_second = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
#         if current_second > order_time_sec + 30:
#             print("Reached")
#             return False
#
#         else:
#             return True


# def BUY_SELL_Function(INSTRUMENT_LTP, INSTRUMENT_symbol): # 1100000005688641
#     print("Inside the buy loop")
#     recent_order = RECENT_ORDER()
#     if not recent_order:
#         print("Inside the Recent order = false block")
#         if 2 < 2:  # datetime.now().hour == 15 & datetime.now().minute == 13:
#
#             if INSTRUMENT_LTP > TARGET_LTP:
#                 print("BUY")
#
#                 data = {
#                     "symbol": INSTRUMENT_symbol,
#                     "qty": 1,
#                     "type": 1,
#                     "side": 1,
#                     "productType": "MARGIN",
#                     "limitPrice": TARGET_LTP + LIMIT_PRICE_TOLERANCE,
#                     "stopPrice": 0,
#                     "validity": "IOC",
#                     "disclosedQty": 0,
#                     "offlineOrder": "False",
#                     "stopLoss": 0,
#                     "takeProfit": 0
#                 }
#
#                 ORDER_STATUS = fyers.place_order(data)
#                 print(ORDER_STATUS)




# ---------------- ORMS - Order Management System -------------------- #


def ORMS ():

    if order_position['overall']['pl_unrealized']==0:
        orms_message = "Urealized overall P&L = 0"
        print(orms_message)

# ---------------- THIS IS THE MAIN LOOP -------------------- #

live_data_change = 0

count = 0

while True:

    custom_message
    # pdb.set_trace()
    count = count + 1
    if count == 1:
        time.sleep(20)

    time.sleep(1)

    NG_March = live_data['MCX:NATURALGAS23MAYFUT']
    NG_April = live_data['MCX:NATURALGAS23JUNFUT']

    arbitrate_spread = NG_April - NG_March

    # Getting current market time in minutes for the day
    now = datetime.datetime.now()

    current_market_time_minute = now.minute

    print(arbitrate_spread)


    if arbitrate_spread >= 20 :


        now = datetime.datetime.now()

        minutes = now.minute
        print(arbitrate_spread)


        # Pinging time marker

        pinging_time_marker_minute = now.minute

        if pinging_time_marker_minute ==  current_market_time_minute:

            print(arbitrate_spread)
            print("inside loop")

            account_sid = 'AC6ebfbd8423f7580af7207ff077a55b07'
            auth_token = 'd491cb111c77266f104c3f6b1096ab9a'
            client = Client(account_sid, auth_token)

            message = client.messages.create(
                from_='whatsapp:+14155238886',
                body='Current spread is >20',
                to='whatsapp:+919059834101'
            )
            time.sleep(3)

            print(message.sid)

    if arbitrate_spread <= 13:


        now = datetime.datetime.now()

        minutes = now.minute
        print(arbitrate_spread)


        # Pinging time marker

        pinging_time_marker_minute = now.minute

        if pinging_time_marker_minute ==  current_market_time_minute:

            print(arbitrate_spread)
            print("inside loop")
 
            account_sid = 'AC6ebfbd8423f7580af7207ff077a55b07'
            auth_token = 'd491cb111c77266f104c3f6b1096ab9a'
            client = Client(account_sid, auth_token)

            message = client.messages.create(
                from_='whatsapp:+14155238886',
                body='Current spread is <13',
                to='whatsapp:+919059834101'
            )
            time.sleep(3)
            print(message.sid)

