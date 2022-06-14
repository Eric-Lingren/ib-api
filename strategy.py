from ibapi.order import *
import ta
import numpy as np
import pandas as pd

from indicators.sma import SMA

class Strategy:
    smaPeriod = 50

    def run(self, bars:list, contract:object, orderId:int, ib:object):
        # #Entry - If we have a higher high, a higher low and we cross the 50 SMA Buy

        #1 - SMA
        closes = []
        for bar in bars:
            closes.append(bar.close)

        sma = SMA.get_latest_sma(period=self.smaPeriod, data=closes)
        print(f'SMA : {sma}')

        #2 - Calculate Higher Highs and Lows
        current_bar = bars[len(bars)-1]
        lastLow = bars[len(bars)-2].low
        lastHigh = bars[len(bars)-2].high
        lastClose = bars[len(bars)-2].close

        # Check Criteria
        if current_bar.high > lastHigh:
            print('ORDER CRITERIA MET')
            print(current_bar.high, lastHigh)

            #Bracket Order 2% Profit Target 1% Stop Loss
            profitTarget = current_bar.close*1.02
            stopLoss = current_bar.close*0.99
            quantity = 1
            bracket = self.bracketOrder(orderId,"BUY",quantity, profitTarget, stopLoss)

            #Place Bracket Order
            for o in bracket:
                print(o)
            #     o.ocaGroup = "OCA_"+str(orderId)
            #     ib.placeOrder(o.orderId,contract,o)
            # orderId += 3

    

    #Bracket Order Setup
    def bracketOrder(self, parentOrderId, action, quantity, profitTarget, stopLoss):
        #Initial Entry
        parent = Order()
        parent.orderId = parentOrderId
        parent.orderType = "MKT"
        parent.action = action
        parent.totalQuantity = quantity
        parent.transmit = False
        # Profit Target
        profitTargetOrder = Order()
        profitTargetOrder.orderId = parent.orderId+1
        profitTargetOrder.orderType = "LMT"
        profitTargetOrder.action = "SELL"
        profitTargetOrder.totalQuantity = quantity
        profitTargetOrder.lmtPrice = round(profitTarget,2)
        profitTargetOrder.parentId = parentOrderId
        profitTargetOrder.transmit = False
        # Stop Loss
        stopLossOrder = Order()
        stopLossOrder.orderId = parent.orderId+2
        stopLossOrder.orderType = "STP"
        stopLossOrder.action = "SELL"
        stopLossOrder.totalQuantity = quantity
        stopLossOrder.parentId = parentOrderId
        stopLossOrder.auxPrice = round(stopLoss,2)
        stopLossOrder.transmit = True

        bracketOrders = [parent, profitTargetOrder, stopLossOrder]
        return bracketOrders
