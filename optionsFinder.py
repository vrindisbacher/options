import yfinance as yf 
import pandas as pd 
import numpy as np
from datetime import datetime

class Options:

    def __init__(self):
        self.sp500 = self.getSP500()
        self.Nasdaq = self.getNasdaq()
        self.DowJones = self.getDowJones()
        print(
            """Possible Function Calls:

            For All Stocks in one or more indices:
            
            findTopOptionsByIndexAndOpenInterest:
                Finds the top options by specified index and open interest:
                default input:
                    Nasdaq=false
                    sp500=false
                    dowjones=false
                    date=None
                    num=5

                If you specify true for all indices, or two it will find the best options (up to length num) 
                comparing across indexes.

            findTopOptionsByIndexAndVolume:
                Finds the top options by specified index and volume:
                    default input:
                        Nasdaq=false
                        sp500=false
                        dowjones=false
                        date=None
                        num=5

                If you specify true for all indices, or two it will find the best options (up to length num) 
                comparing across indexes.

            For a specific stock:

            topOptionsByInterest
                - optional date to specify how far out to consider.
                  Date must be in 'YYYY-MM-DD'.If you don't specify a date, it will
                  return first expiry date
                - num - change the number of contracts to return. default is 5


            topOptionsByVolume:
            
                - optional date to specify how far out to consider.
                  Date must be in 'YYYY-MM-DD'.If you don't specify a date, it will
                  return first expiry date
                - num - change the number of contracts to return. default is 5


            All of these functions return:
                - a list of tuples where 
                ind 0: the openInterest or volume on the option
                ind 1: all the contract information
        """
            )
            

    def getSP500(self):
        payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = payload[0]
        return df['Symbol'].values.tolist()

    def getNasdaq(self):
        payload = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
        df = payload[3]
        return df['Ticker'].values.tolist()
    
    def getDowJones(self):
        payload = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
        df = payload[1]
        return df['Symbol'].values.tolist()


    def findTopOptionsByIndexAndOpenInterest(self, Nasdaq=False, sp500=False, DowJones=False, date=None, num=5):
        """
        Finds the top options by specified index:
        default input:
            Nasdaq=false
            sp500=false
            dowjones=false
            date=None
            num=5

        If you specify true for all, or two it will find the best options (up to length num) 
        comparing across indexes
        """
        toSearch = []
        if Nasdaq:
            toSearch += self.Nasdaq
        if sp500:
            toSearch += self.sp500
        if DowJones:
            toSearch += self.DowJones

        contracts = []

        for ticker in toSearch:
            try:
                topNum = self.topOptionsByInterest(ticker, num, date)
                for contract in topNum:
                    if len(contracts) < num:
                        contracts.append(contract)
                    else:
                        lowestIndx = 0
                        currMin = float("inf")

                        for i in range(len(contracts)):
                            if contracts[i][0] < currMin:
                                lowestIndx = i
                                currMin = contracts[i][0]
                        
                        if contract[0] > contracts[lowestIndx][0]:
                            contracts[lowestIndx] = contract
            except:
                pass

        return contracts             


    def findTopOptionsByIndexAndVolume(self, Nasdaq=False, sp500=False, DowJones=False, date=None, num=5):
        """
        Finds the top options by specified index:
        default input:
            Nasdaq=false
            sp500=false
            dowjones=false
            date=None
            num=5

        If you specify true for all, or two it will find the best options (up to length num) 
        comparing across indexes
        """
        toSearch = []
        if Nasdaq:
            toSearch += self.Nasdaq
        if sp500:
            toSearch += self.sp500
        if DowJones:
            toSearch += self.DowJones

        contracts = []

        for ticker in toSearch:
            try:
                topNum = self.topOptionsByVolume(ticker, num, date)
                for contract in topNum:
                    if len(contracts) < num:
                        contracts.append(contract)
                    else:
                        lowestIndx = 0
                        currMin = float("inf")

                        for i in range(len(contracts)):
                            if contracts[i][0] < currMin:
                                lowestIndx = i
                                currMin = contracts[i][0]
                        
                        if contract[0] > contracts[lowestIndx][0]:
                            contracts[lowestIndx] = contract
            except:
                pass
        return contracts                       
            

    def findMaxCallsOrPutsByInterest(self, optionChain, contracts, num):
        """
        A helper function of topOptionsByInterest
        """
        index = 0
        for data in optionChain['openInterest']:
            if len(contracts) < num:
                contracts.append((data, optionChain.loc[index]))
            else:                    
                if data is not None:
                    lowestIndx = 0
                    currMin = float("inf")

                    for i in range(len(contracts)):
                        if contracts[i][0] < currMin:
                            lowestIndx = i
                            currMin = contracts[i][0]

                    if data > contracts[lowestIndx][0]:
                        contracts[lowestIndx] = (data, optionChain.loc[index])

            index += 1

        return contracts

    def findMaxCallsOrPutsByVolume(self, optionChain, contracts, num):
        """
        A helper function of topOptionsByVolume
        """
        index = 0
        for data in optionChain['volume']:
            if len(contracts) < num:
                contracts.append((data, optionChain.loc[index]))
            else:                    
                if data is not None:
                    lowestIndx = 0
                    currMin = float("inf")

                    for i in range(len(contracts)):
                        if contracts[i][0] < currMin:
                            lowestIndx = i
                            currMin = contracts[i][0]

                    if data > contracts[lowestIndx][0]:
                        contracts[lowestIndx] = (data, optionChain.loc[index])

            index += 1

        return contracts


    def topOptionsByInterest(self, ticker, num=5, date=None):
        """ 
        Highest open interest on a stocks option chain: 
            - optional date to specify how far out to consider.
              Date must be in 'YYYY-MM-DD'.If you don't specify a date, it will
              return first expiry date
            - num - change the number of contracts to return. default is 5

        Returns:
            - a list of tuples where 
            ind 0: the openInterest on the option
            ind 1: all the contract information
        """
        stock = yf.Ticker(ticker)
        expDates = stock.options
        if date:
            expToFind = []
            for exp in expDates:
                if datetime.fromisoformat(exp) < datetime.fromisoformat(date):
                    expToFind.append(exp)
        else:
            expToFind = [expDates[0]]

        for exp in expToFind:
            optionChain = stock.option_chain(exp)
            calls = optionChain.calls
            puts = optionChain.puts
            topOptions = self.findMaxCallsOrPutsByInterest(calls, [], num)
            topOptions = self.findMaxCallsOrPutsByInterest(puts, topOptions, num)
        
        return topOptions


    def topOptionsByVolume(self, ticker, num=5, date=None):
        """
         Highest volume on a stocks option chain: 
            - optional date to specify how far out to consider.
              Date must be in 'YYYY-MM-DD'.If you don't specify a date, it will
              return first expiry date
            - num - change the number of contracts to return. default is 5

        Returns:
            - a list of tuples where 
            ind 0: the volume on the option
            ind 1: all the contract information
        """
        stock = yf.Ticker(ticker)
        expDates = stock.options
        if date:
            expToFind = []
            for exp in expDates:
                if datetime.fromisoformat(exp) < datetime.fromisoformat(date):
                    expToFind.append(exp)
        else:
            expToFind = [expDates[0]]

        for exp in expToFind:
            optionChain = stock.option_chain(exp)
            calls = optionChain.calls
            puts = optionChain.puts
            topOptions = self.findMaxCallsOrPutsByVolume(calls, [], num)
            topOptions = self.findMaxCallsOrPutsByVolume(puts, topOptions, num)
        
        return topOptions

