
#Imports
import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
import pytz
import math
from datetime import datetime
import threading
import time

from bar import Bar
from config import Config
from strategy import Strategy

#Vars
orderId = 1


#Class for Interactive Brokers Connection
class IBApi(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self, self)

    #* Load Historical Data
    def historicalData(self, reqId, bar):
        try:
            bot.on_bar_update(reqId, bar, False)
        except Exception as e:
            print(e)

    #* On Realtime Bar after historical data finishes
    def historicalDataUpdate(self, reqId, bar):
        try:
            bot.on_bar_update(reqId, bar, True)
        except Exception as e:
            print(e)

    #* On Historical Data End
    def historicalDataEnd(self, reqId, start, end):
        print(f'{reqId} - Historical Data Loaded')

    #* Get next order id we can use
    def nextValidId(self, nextorderId):
        global orderId
        orderId = nextorderId

    #* Notification Handler
    def error(self, reqId, errorCode, errorMsg):
        print(f'NOTIFY - {reqId} {errorCode} {errorMsg}')
        #TODO - Notify when disconnected / Auto Reconnect



#Bot Logic
class Bot:
    global orderId
    ib = None
    config = None
    contract = Contract()
    currentBar = Bar()
    strategy = Strategy()
    bars = []
    reqId = 1
    initial_bar_time = datetime.now().astimezone(pytz.timezone("America/New_York"))

    def __init__(self):
        #* Connect to IB on init
        self.ib = IBApi()
        self.ib.connect("127.0.0.1", 7497,1)
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)

        #* Set Configs:
        self.set_configs() 

        #* Create our IB Contract Object:
        self.set_contract()

        # self.symbol = input("Enter the symbol you want to trade : ")
        # self.bar_size = int(input("Enter the bar_size you want to trade in minutes : "))

        #* Triggers nextValidId function to run:
        self.ib.reqIds(-1) 

        #* Request Market Data:
        self.ib.reqHistoricalData(self.reqId, self.contract,"","1 D", self.config.bar_size_str,"BID",1,1,True,[])
    
    
    #* Listen to socket in separate thread
    def run_loop(self):
        self.ib.run()


    def set_configs(self):
        self.config = Config(
        symbol='EUR', 
        secType='CASH', 
        exchange='SMART', 
        primaryExchange='IDEALPRO', 
        currency='USD',
        bar_size_int = 1
    )

    def set_contract(self):
        self.contract.symbol = self.config.symbol
        self.contract.secType = self.config.secType
        self.contract.exchange = self.config.exchange
        self.contract.primaryExchange = self.config.primaryExchange
        self.contract.currency = self.config.currency


    #* Pass realtime bar data back to our bot object
    def on_bar_update(self, reqId, bar, is_real_time):
        global orderId
        if is_real_time == False:
            '''
            Load in Historical Data
            '''
            self.instantiate_new_bar(bar)
            self.update_existing_bar( bar)
            self.conclude_existing_bar(bar)
        else:
            '''
            Process Realtime Bar
            '''
            self.update_existing_bar(bar) #* Update current bar with new data
            
            #* Checks if the current bar has closed:
            bar_time = datetime.strptime(bar.date,"%Y%m%d %H:%M:%S").astimezone(pytz.timezone("America/New_York"))
            minutes_diff = (bar_time - self.initial_bar_time).total_seconds() / 60.0
            self.currentBar.date = bar_time
            
            if (minutes_diff > 0 and math.floor(minutes_diff) % self.config.bar_size_int == 0):
                '''
                On Bar Close:
                '''
                self.initial_bar_time = bar_time #* Reset timer to build new bar
                self.conclude_existing_bar(bar) #* Close Out Existing Realtime Bar

                print("\nNew bar!")
                print(f'Date {self.currentBar.date} O: {self.currentBar.open} H {self.currentBar.high} L {self.currentBar.low} C {self.currentBar.close}')
                
                #! Insert Strategy Here
                self.strategy.run(bars=self.bars, contract=self.contract, orderId=orderId, ib=self.ib)
                
                # Check Criteria
                # if (bar.close > lastHigh
                #     and self.currentBar.low > lastLow
                #     and bar.close > str(self.sma[len(self.sma)-1])
                #     and lastClose < str(self.sma[len(self.sma)-2])):
                    #Bracket Order 2% Profit Target 1% Stop Loss
                    # profitTarget = bar.close*1.02
                    # stopLoss = bar.close*0.99
                    # quantity = 1
                    # bracket = self.bracketOrder(orderId,"BUY",quantity, profitTarget, stopLoss)
                    # contract = Contract()
                    # contract.symbol = self.symbol.upper()
                    # contract.secType = "STK"
                    # contract.exchange = "SMART"
                    # contract.currency = "USD"
                    # #Place Bracket Order
                    # for o in bracket:
                    #     o.ocaGroup = "OCA_"+str(orderId)
                    #     self.ib.placeOrder(o.orderId,contract,o)
                    # orderId += 3

                self.instantiate_new_bar(bar) #* Create a New Realtime Bar


    #* Create a New Realtime Bar
    def instantiate_new_bar(self, bar):
        self.currentBar = Bar()
        self.currentBar.open = bar.open


    #* Update an Existing Realtime Bar
    def update_existing_bar(self, bar):
        if (self.currentBar.open == 0):
            self.currentBar.open = bar.open
        if (self.currentBar.high == 0 or bar.high > self.currentBar.high):
            self.currentBar.high = bar.high
        if (self.currentBar.low == 0 or bar.low < self.currentBar.low):
            self.currentBar.low = bar.low


    #* Close Out an Existing Realtime Bar
    def conclude_existing_bar(self, bar):
        #* Append Closed Value to Bar:
        self.currentBar.close = bar.close
        #* Add Completed Bar To Array:
        self.bars.append(self.currentBar)


#* Start Bot
if __name__ == "__main__":
    bot = Bot()