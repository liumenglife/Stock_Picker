##
## Innovative Comparison Calculator by Elias
##
import math
import random
from pprint import pprint
import json
import unicodedata
import feedparser
import bs4
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import datetime
import argparse
import threading
import os
import time
import winsound
import webbrowser
import json
import csv
from os import listdir
from os.path import isfile, join
from stockObj import stock
from operator import itemgetter
import requests


##user_agents = []
##with open("user_agents.txt", 'rb') as uaf:
##    for ua in uaf.readlines():
##        if ua:
##            user_agents.append(ua.strip()[1:-1-1])
##print user_agents[:5]
##user_agents = [[("User-agent", ua)] for ua in user_agents]
##random.shuffle(user_agents)
##print user_agents[:5]
##
##ua = random.choice(user_agents)
##
##url = "http://www.google.com/finance/historical?output=csv&q=LON:LLOY"
##
##stockFile = urllib.URLopener()
##stockFile.addheaders = ua
##stockFile.retrieve(url, "testfile.csv")
##print stockFile.addheaders


###Not in use
###PROXY HERE
##proxies = {}
####
##url = "http://www.google.com/finance/historical?"
##params = {"output": "csv", "q": "LON:LLOY"}
##headers = {"Connection" : "close", "User-Agent" : ua}
##r = requests.get(url, proxies = proxies, params = params, headers = headers)
##csvText = r.text.split("\n")
##csvText = [rowItem.split(",") for rowItem in csvText]
##print "a"
##if csvText[0][0] == "Date":
##    with open("testfile.csv", 'wb') as csvfile:
##        spamWriter = csv.writer(csvfile)
##        spamWriter.writerows(csvText)
##else:
##    print "Proxy or other file retrieve error"



#list of available spreadsheets from nasdaq.com (same format)

class stockSystem(object):
    #stockCodeList is a list of tuples [(stock code, stock url)]
    def __init__(self, __watchList, __exchangeCode, __stockObjList = [], dateList = []
                 , __watchListObjList = [], codeList = [], __sectorDict = {}, americaExList = []):
        self.__watchList = __watchList
        for item in self.__watchList:
            item = item.upper()
        self.__stockObjList = []
        self.dateList = []
        self.__watchListObjList = []
        self.codeList = []
        #sector dict holds objects, not codes
        self.__sectorDict = {}
        self.americaExList = ["NASDAQ", "NYSE", "AMEX"]
        self.__exchangeCode = __exchangeCode.upper()
        if self.__exchangeCode == "LSE":
            self.__exchangeCode = "LON"
        random.seed()
        self.create_date_list("01-01-2000")
        
##        for stockItem in stockCodeList:
##            temp = stock(stockItem[0], stockItem[1], False, None, None)
##            self.__stockObjList.append(temp)
##        self.search_feeds_loop()


    #Creates list of dates for comparison
    def create_date_list(self, startDate):
        todaysDate = str(datetime.datetime.now().date())
        todaysDateNewFormat = todaysDate[8:] + "-" + todaysDate[5:7] + "-" + todaysDate[:4]
        start = datetime.datetime.strptime(startDate, '%d-%m-%Y').date()
        end = datetime.datetime.strptime(todaysDateNewFormat, '%d-%m-%Y').date()
        step = datetime.timedelta(days=1)

        while start <= end:
            self.dateList.append(str(start))
            start += step
        return self.dateList

            
    #For creating all stock objects, and performing any necessary operation to all of them
    def init_stock_objects(self, date):
        print("The current number of stocks in the system is", len(self.__stockObjList))
        print("Adding stocks from", self.__exchangeCode, "from the", date)
        files = []
        path = os.path.abspath("Stock Data/" + self.__exchangeCode + "/" + date)
        print("Checking for stocks in path", path)
        #try:
        files = [f for f in listdir(path) if isfile(join(path, f))]
##        #except:
##            print "ERROR: path for given date", date, "not present"
##            return False
        print(len(files), "Stocks found in path")
        
        stockNamesList = []
        for x in files:
            splitName = x.split(".")
            name = ""
            for y in range(len(splitName) - 1):
                name += splitName[y]
                if y < len(splitName) - 2:
                    name += "."
            stockNamesList.append(name)
        print("Creating stock objects")

        count = 1
        for x in stockNamesList:
##            if count % 200 == 0:
##                print count, "stocks objects created so far"
            #print "adding", x, "to dictionary"
            self.__stockObjList.append(stock(self.__exchangeCode, x))
            count += 1
        #[add_to_data_dict(exchangeName, date, x) for x in stockNamesList]
        print(count, "stock objects created")
        print(self.__exchangeCode, date, "created, The new number of stock objects in system is", len(self.__stockObjList))

        for item in self.__stockObjList:
            item.RSS_init()
            self.codeList.append(item.return_stock_code())


    def init_stocks_RSS(self):
        print("Loading", len(self.__watchList), "stocks from watchlist for RSS monitoring")
        for stockItem in self.__stockObjList:
            if stockItem.return_stock_code() in self.__watchList:
                stockItem.RSS_init()
                self.__watchListObjList.append(stockItem)

    def load_stock_charts(self, date):
        print("Loading available stock price charts")
        errorList = []
        for stockItem in self.__stockObjList:
            try:
                result = stockItem.load_price_sheet(self.dateList, date)
                if result:
                    print(stockItem.return_stock_code(), "loaded")
                if result == "Empty":
                    print(stockItem.return_stock_code(), "found empty")
            except:
                print("ERROR with:", stockItem.return_stock_code() + ",deleting from obj list")
                errorList.append(stockItem.return_stock_code())
                del self.__stockObjList[self.__stockObjList.index(stockItem)]
        print("Price chart error/exclusion list:")
        print(errorList)
##            except:
##                print "ERROR with stock", stockItem.return_stock_code()


    def __init_sector_dict(self):
        self.__sectorDict = {}
        if self.__exchangeCode == "LON":
            for stockObjItem in self.__stockObjList:
                superSector = stockObjItem.rad("Supersector")
                sector = stockObjItem.rad("Sector")
                subSector = stockObjItem.rad("Subsector")

                if superSector == False:
                    print("ERROR with superSector dict for", stockObjItem.return_stock_code, "given value of 'ERROR'")
                    superSector = "ERROR"
                if sector == False:
                    print("ERROR with sector dict for", stockObjItem.return_stock_code, "given value of superSector")
                    sector = superSector
                if subSector == False:
                    print("ERROR with subSector dict for", stockObjItem.return_stock_code, "given value of sector/superSector")
                    subSector = sector
            
                if superSector not in self.__sectorDict:
                    self.__sectorDict[superSector] = {}
                if sector not in self.__sectorDict[superSector]:
                    self.__sectorDict[superSector][sector] = {}
                if subSector not in self.__sectorDict[superSector][sector]:
                    self.__sectorDict[superSector][sector][subSector] = []
                self.__sectorDict[superSector][sector][subSector].append(stockObjItem)
                
            superSectorCount = 0
            sectorCount = 0
            subSectorCount = 0
            itemCount = 0
            testList = []
            for superItem in self.__sectorDict:
                superSectorCount += 1
                for item in self.__sectorDict[superItem]:
                    sectorCount += 1
                    for subItem in self.__sectorDict[superItem][item]:
                        subSectorCount += 1
                        for listItem in self.__sectorDict[superItem][item][subItem]:
                            testList.append(listItem)
                            itemCount += 1
    ##                    print superItem, item, subItem
            print("Sector dict created")
            print("Supersector count:", superSectorCount)
            print("Sector count:", sectorCount)
            print("subSectorCount:", subSectorCount)
            print("itemCount", itemCount)
            print("Len obj list:", len(self.__stockObjList))
            
        elif self.__exchangeCode in self.americaExList:
            for stockObjItem in self.__stockObjList:
                sector = stockObjItem.rad("Sector")
                industry = stockObjItem.rad("industry")
                
                if sector == False:
                    print("ERROR with sector dict for", stockObjItem.return_stock_code, "given value of 'ERROR'")
                    sector = "ERROR"
                if industry == False:
                    print("ERROR with industry dict for", stockObjItem.return_stock_code, "given value of sector")
                    industry = sector

                if sector not in self.__sectorDict:
                    self.__sectorDict[sector] = {}
                if industry not in self.__sectorDict[sector]:
                    self.__sectorDict[sector][industry] = []
                self.__sectorDict[sector][industry].append(stockObjItem)
                
                sectorCount = 0
                industryCount = 0
                itemCount = 0
                testList = []
                for sectorItem in self.__sectorDict:
                    sectorCount += 1
                    for industryItem in self.__sectorDict[sectorItem]:
                        industryCount += 1
                        for listItem in self.__sectorDict[sectorItem][industryItem]:
                            testList.append(listItem)
                            itemCount += 1
    ##                    print superItem, item, subItem
            print("Sector dict created")
            print("Sector count:", sectorCount)
            print("industry count:", industryCount)
            print("itemCount", itemCount)
            print("Len obj list:", len(self.__stockObjList))


    def sector_dict_search(self, superSector, sector, subSector, echo, openBrowser):
        objReturnList = self.__sectorDict[superSector][sector][subSector]
        returnList = []
        for item in objReturnList:
            returnList.append((item.return_stock_code(), float(item.rad("Mkt Cap \xa3m")), item))
        returnList = sorted(returnList, key=itemgetter(1))
        if echo == True:
            print("sector dict search results:")
            for item in returnList:
                print(item[:-1])
        if openBrowser == True:
            for item in returnList:
                item[2].open_google_page()
        return returnList     
            

    def SD_test_func(self, previous, returnCount):
        objResultList = []
        for stockObj in self.__stockObjList:
            difference = stockObj.return_weighted_average_SD(previous, 7, 8, False)
            #difference = abs(stockObj.return_column_SD(previous, 6, False) + stockObj.return_column_SD(previous, 9, False))/2
            if self.__exchangeCode == "LON":
                if stockObj.checkVolume(previous) == True and stockObj.rad("Mkt Cap \xa3m") != "0":
                    objResultList.append((stockObj.return_stock_code(), difference, stockObj.rad("Mkt Cap \xa3m"),
                                          stockObj.rad("Supersector"), stockObj.rad("Sector"), stockObj.rad("Subsector"),
                                          stockObj.rad("Google Finance Url")))
            elif self.__exchangeCode in self.americaExList:
                if stockObj.checkVolume(previous) == True and stockObj.rad("MarketCap") != "n/a":
                    objResultList.append((stockObj.return_stock_code(), difference, stockObj.rad("MarketCap"),
                                          stockObj.rad("Sector"), stockObj.rad("industry"),
                                          stockObj.rad("Google Finance Url")))
        objResultList = sorted(objResultList, key=itemgetter(1))
        while objResultList[0] == False:
            del objResultList[0]
        try:
            return objResultList[-returnCount:]
        except:
            return objResultList
            
    #Goes through each stock object and adds a associate variable called "SD5" (or whatever the previous count is)
    #Creates a new dictionary to hold the SD values
    #Search is a list of the various sections it is placed under
    def calculate_sector_SDs(self, previous, column, search, normalised):
        modifier = ""
        try:
            self.__stockObjList[0].rad("SD" + str(previous))
            modifier = "(2)"
        except:
            pass
        for stockItem in self.__stockObjList:
            stockItem.add_associate_data("SD" + str(previous) + modifier, stockItem.return_weighted_average_SD(previous, column, False, False))
        SDDict = {}
        for superDictKey in self.__sectorDict:
            SDDict[superDictKey] = {}
            for dictKey in self.__sectorDict[superDictKey]:
                SDDict[superDictKey][dictKey] = {}
                for subDictKey in self.__sectorDict[superDictKey][dictKey]:
                    SDDict[superDictKey][dictKey][subDictKey] = [0.0, 0]
##        print SDDict
        count = 0
        for stockItem in self.__stockObjList:
            SDDict[stockItem.rad("Supersector")][stockItem.rad("Sector")][stockItem.rad("Subsector")][0] += stockItem.rad("SD" + str(previous) + modifier)
            SDDict[stockItem.rad("Supersector")][stockItem.rad("Sector")][stockItem.rad("Subsector")][1] += 1

        if search != False:
            if search.lower() == "top":
                topList = []
                for superDictKey in SDDict:
                    for dictKey in SDDict[superDictKey]:
                        for subDictKey in SDDict[superDictKey][dictKey]:
                            if normalised == True:
                                SDDict[superDictKey][dictKey][subDictKey][0] /= SDDict[superDictKey][dictKey][subDictKey][1]
                            topList.append((superDictKey, dictKey, subDictKey, SDDict[superDictKey][dictKey][subDictKey][0]))
                topList = sorted(topList, key=itemgetter(3))
                return SDDict,topList
            try:
                return SDDict, SDDict[search[0].lower()][search[1].lower()][search[2].lower()]
            except:
                print("Key error with search, check sectors have correct names and run again")
                return SDDict
        print("ERROR: Hmm, this shouldn't be being printed...")
        return SDDict
                

    #Don't run close to midnight (maybe(lol(incorrect use of parentheses))
    def update_stock_spreadsheets(self, override, startCode):
        todaysDate = str(datetime.datetime.now().date())
        
        print("Loading stock codes from " + self.__exchangeCode)
        #Currently only configured for LSE stocks
        #csvUrl = "http://www.londonstockexchange.com/statistics/companies-and-issuers/list-of-all-securities-ex-debt.xls"
        listingsPath = "Stock Data/" + self.__exchangeCode + "/Listings/" + self.__exchangeCode + " listings " + todaysDate + ".csv"
        stockCodeList = []
        if self.__exchangeCode == "LON":
            with open(listingsPath, "rb") as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    stockCodeList.append(row[7].upper())
            stockCodeList = stockCodeList[7:]
            stockCodeList.sort()
            #Gets rid of stocks that don't work for the url
            stockCodeList = stockCodeList[215:]
        #http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download
        elif self.__exchangeCode in self.americaExList:
            if isfile(listingsPath) == False:
                url = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=" + self.__exchangeCode.lower() + "&render=download"
                stockFile = urllib.request.URLopener()
                stockFile.retrieve(url, listingsPath)
            with open(listingsPath, "rb") as csvFile:
                reader = csv.reader(csvFile)
                for row in reader:
                    stockCodeList.append(row[0].upper())
            del stockCodeList[0]
            stockCodeList.sort()
            
           
        codeCounter = 0 
        #Update this bit; some weird bug stopping me from using range(len())
        while codeCounter < len(stockCodeList):
            try:
                while stockCodeList[codeCounter][-1] == " ":
                    stockCodeList[codeCounter] = stockCodeList[codeCounter][:-1]
            except:
                print("Error with", stockCodeList[codeCounter])
            #print codeCounter, "'" + stockCodeList[codeCounter] + "'"
            codeCounter += 1
        
        print("Checking directory")
        savePath = os.path.abspath("Stock Data/" + self.__exchangeCode + "/" + todaysDate)
        if os.path.exists(savePath):
            if override == False:
                print("ERROR: directory already exists and no override given")
                return False
            print("Proceeding with directory override")
        else:
            os.makedirs(savePath)
            print("Creating directory for new day")
        #dataList = sorted(dataList, key=itemgetter(7))

        print("Retrieving stock spreadsheets (from google)")
        codeCounter = 0
        failCounter = 0

        ###########################################################needs updating
        if startCode != False:
            startCode = startCode.upper()
            try:
                codeCounter = stockCodeList.index(startCode) + 1
            except:
                print("ERROR: starting stock name '" + startCode + "' not found for downloading data")
                return False
        ###########################################################needs updating
        
        while codeCounter < list(range(len(stockCodeList) - 1)):
            try:
                stockCode = stockCodeList[codeCounter]
            except:
                print("Update complete; stored under /Stock Data/" + self.__exchangeCode + "/" + todaysDate)
                return True
            savePath = os.path.abspath("Stock Data/" + self.__exchangeCode + "/" + todaysDate) + "/" + stockCode + ".csv"
            url = "http://www.google.com/finance/historical?output=csv&q=" + self.__exchangeCode + ":" + stockCode.lower()
            try:
                stockFile = urllib.request.URLopener()
                stockFile.retrieve(url, savePath)
                print("Stock found and csv downloaded for '" + stockCode + "'")
                failCounter = 0
            except:
                print("No stock data found for '" + stockCode + "'")
                failCounter += 1
            if failCounter >= 25:
                print(time.ctime(), "google blocking requests detected; pausing for 46-49 minutes")
                time.sleep(60 * (46 + 3 * random.random()))
                codeCounter -= 26
                failCounter = 0
            codeCounter += 1


    def create_daily_pickings(self, inpList, openBrowser, inpDate):
        inpList = sorted(inpList, key=itemgetter(1))
        inpList.insert(0, ["Code", "SD", "Mkt Cap", "Supersector", "Subsector", "Subsector", "Google Finance Url"])
        savePath = os.path.abspath("Stock Data/" + self.__exchangeCode + "/Daily Pickings/" + inpDate)
        if os.path.exists(savePath) == False:
            os.makedirs(savePath)
        if isfile(savePath + "/" + inpDate + " Pickings.csv") == True:
            print("File already present for pickings, passings creation:", self.__exchangeCode, inpDate)
        else:
            print("Creating new pickings file:", self.__exchangeCode, inpDate)
            with open(savePath + "/" + inpDate + " Pickings.csv", 'wb') as csvfile:
                spamWriter = csv.writer(csvfile)
                spamWriter.writerows(inpList)
        if openBrowser == True:
            stockCodes = []
            for listItem in inpList:
                stockCodes.append(listItem[0])
            for item in self.__stockObjList:
                testCode = item.return_stock_code()
                if testCode in stockCodes:
    ##                item.download_daily_picking(stockCodes.index(testCode), False)
                    item.open_google_page()
    

    #TODO: adds lots of useful info to the stock objects
    def add_stock_info(self, inpDate):
        dataList = []
        listingsPath = "Stock Data/" + self.__exchangeCode + "/Listings/" + self.__exchangeCode + " listings " + inpDate + ".csv"
        with open(listingsPath, "rb") as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                dataList.append(row)
        if self.__exchangeCode == "LON":
            for item in dataList:
                item[7] = item[7].upper()
            dataTitles = dataList[6][:18]
        elif self.__exchangeCode in self.americaExList:
            dataTitles = dataList[0][:9]
            del dataList[0]
            for item in dataList:
                item[0] = item[0].upper()
                if item[3] != "n/a":
                    item[3] = float(item[3][1:-1])
        print("-------------------------------------------------------------")
        print("Data Titles:")
        print(dataTitles)
        print("-------------------------------------------------------------")
        #dataList = dataList[215:]
        dataDict = {}
##        for dataItem in dataList:
##            print dataItem
        for dataItem in dataList:
            codeEdit = ""
            if self.__exchangeCode == "LON":
                codeEdit = dataItem[7]
            elif self.__exchangeCode in self.americaExList:
                codeEdit = dataItem[0]
            try:
##                print codeEdit
                while codeEdit[-1] == " ":
                    codeEdit = codeEdit[:-1]
                #print codeEdit
                dataDict[codeEdit] = {}
                dataTitleCounter = 0
                while dataTitleCounter < len(dataTitles):
                    dataDict[codeEdit][dataTitles[dataTitleCounter]] = dataItem[dataTitleCounter]
                    dataTitleCounter += 1
            except:
                pass

        #print dataDict
                
        for stockObj in self.__stockObjList:
            stockCode = str(stockObj.return_stock_code())
##            try:
            for dataKey in dataDict[stockCode]:
                try:
                    stockObj.add_associate_data(dataKey, dataDict[stockCode][dataKey].lower())
                except:
                    stockObj.add_associate_data(dataKey, dataDict[stockCode][dataKey])
##                print stockCode
##            except:
##                print "ERROR with", stockCode

        self.__init_sector_dict()


    def print_stocks_in_similar_sector(self, stockCode):
        print("Finding stocks in similar sectors to", stockCode) 
        stockItem = self.return_stock_object_from_stock_code(stockCode)
        if stockItem == False:
            print("")
            print("Stock code not found in system object list")
            return False
        if self.__exchangeCode == "LON":
            superSector = stockItem.retrieve_associate_data("Supersector")
            print("Supersector:", superSector)
            superSectorList = []
            sector = stockItem.retrieve_associate_data("Sector")
            print("Sector:", sector)
            sectorList = []
            subSector = stockItem.retrieve_associate_data("Subsector")
            print("Supersector:", subSector)
            print("")
            subSectorList = self.__sectorDict[superSector][sector][subSector]
            
            for sectorItem in self.__sectorDict[superSector]:
                for listItem in self.__sectorDict[superSector][sectorItem]:
                    superSectorList += self.__sectorDict[superSector][sectorItem][listItem]
            for listItem in self.__sectorDict[superSector][sectorItem]:
                sectorList += self.__sectorDict[superSector][sectorItem][listItem]
                
            superSectorList = [item.return_stock_code() for item in superSectorList]
            sectorList = [item.return_stock_code() for item in sectorList]
            subSectorList = [item.return_stock_code() for item in subSectorList]
                
            del superSectorList[superSectorList.index(stockCode)]
            del sectorList[sectorList.index(stockCode)]
            del subSectorList[subSectorList.index(stockCode)]

            print("Supersector list:")
            for item in superSectorList:
                print(item)
            print("Length:", len(superSectorList))
            print("")
            print("Sector list:")
            for item in sectorList:
                print(item)
            print("Length:", len(sectorList))
            print("")
            print("Subsector list:")
            for item in subSectorList:
                print(item)
            print("Length:", len(subSectorList))
            print("")
            print("Complete")
            
        elif self.__exchangeCode in self.americaExList:
            stockItem = self.return_stock_object_from_stock_code(stockCode)
            sector = stockItem.rad("Sector")
            print("Sector:", sector)
            industry = stockItem.rad("industry")
            print("industry:", industry)
            
            similarSectorList = []
            similarIndustryList = self.__sectorDict[sector][industry]
            for sectorItem in self.__sectorDict[sector]:
                similarSectorList += self.__sectorDict[sector][sectorItem]
            similarSectorList = [item.return_stock_code() for item in similarSectorList]
            similarIndustryList = [item.return_stock_code() for item in similarIndustryList]
                
            del similarSectorList[similarSectorList.index(stockCode)]
            del similarIndustryList[similarIndustryList.index(stockCode)]
            
            print("Similar sector List:")
            for item in similarSectorList:
                print(item)
            print("Length:", len(similarSectorList))
            print("")
            print("Similar Industry List:")
            for item in similarIndustryList:
                print(item)
            print("Length:", len(similarIndustryList))
            print("")
            print("Complete")
            

    def temp_func(self, stockCode):
        print(stockCode, "      ", self.return_stock_object_from_stock_code(stockCode).retrieve_associate_data("Supersector"))
        #print "         ", self.return_stock_object_from_stock_code(stockCode).retrieve_associate_data("Sector")
        #print "         ", self.return_stock_object_from_stock_code(stockCode).retrieve_associate_data("Subsector")

    def return_stock_object_from_stock_code(self, stockCode):
        for stockItem in self.__stockObjList:
            if stockItem.return_stock_code() == stockCode:
                return stockItem
        return False

    def add_RSS_stocks(self, inpList):
        for item in inpList:
            self.__watchList.append(item)

        
    def RSS_search_feeds_loop(self):
        print("Searching...", end=' ')
        while True:
            for stockItem in self.__watchListObjList:
                if stockItem.RSS_check_for_updates() == False:
                    print("#", end=' ')
                else:
                    print("Resuming normal function...", end=' ')
                time.sleep(7*random.random())

    #Returns a list of the objects
    def RSS_check_for_keywords(self, codeList, keywords, requiredNum):
        objSearchList = []
        if codeList == True or codeList == False:
            objSearchList = self.__stockObjList
        else:
            for codeItem in codeList:
                objSearchList.append(self.return_stock_object_from_stock_code(codeItem))
                                     
        returnList = []
        counter = 0
        lenObjList = str(len(objSearchList))
        for stockTest in objSearchList:
            if stockTest.RSS_str_search(keywords, requiredNum, False)[0] == True:
                returnList.append(stockTest.return_stock_code())
                print("RESULT:", stockTest.return_stock_code())
                #print stockTest
            else:
                print(str(counter) + "/" + lenObjList)
##            print stockTest.return_stock_code(), stockTest.RSS_str_search(keywords, requiredNum, False)
            counter += 1
        print("----------------------------------")
        print("RSS search results:")
        print("----------------------------------")
        for item in returnList:
            print(item)
        return returnList


    def check_for_crossover(self, inputList, requirement):
##        inputList = []
##        for item in self.__stockObjList:
##            inputList.append(item.return_stock_code())
        stockObjList = []
        for stockCode in inputList:
            stockObjList.append(self.return_stock_object_from_stock_code(stockCode))

##        print len(stockObjList)
##        for item in stockObjList:
##            print item.return_stock_code()
            
        returnList = []
        for stockItem in stockObjList:
##            try:
##            print stockItem
##            print stockItem.print_data_line(0, True)
##            except:
##                pass
            tempList = stockItem.locate_crossovers(11, 12)
            if tempList != False:
                if len(tempList) > 0:
                    if tempList[0] <= requirement:
                        returnList.append(stockItem.return_stock_code())
        print("----------------------------------")
        print("Crossover Results:")
        print("----------------------------------")
        for item in returnList:
            print(item)
        return returnList
                    
            
    def test_func(self, superSector, sector, subSector, previous):
        print("Initiating test func")
        returnList = []
        for stockItem in self.__sectorDict[superSector][sector][subSector]:
            returnList.append((stockItem.return_stock_code(), stockItem.return_column_SD(previous, 1, False, False) + stockItem.return_column_SD(previous, 4, False, False), stockItem.return_column_SD(previous, 6, False, False) + stockItem.return_column_SD(previous, 9, False, False)))
        return returnList

    def volatility_search(self, previous, inpDate):
        changes = self.calculate_sector_SDs(previous, 9, "top", True)[1]
        actual = self.calculate_sector_SDs(previous, 4, "top", False)[1]
        fileText = ""
        jsonDict = {}
        print("Actual cash flow result, sorted:")
        print("")
        fileText += "Actual cash flow result, sorted:\n"
        jsonDict["actual"] = actual
        for item in actual:
            print(item)
            fileText += str(item) + "\n"
        print("")
        print("---------------------------------------------------------")
        print("Normalised cash flow result, sorted:")
        print("")
        fileText += "---------------------------------------------------------\n"
        fileText += "Normalised cash flow result, sorted:\n"
        jsonDict["changes"] = changes
        for item in changes:
            print(item)
            fileText += str(item) + "\n"
        print("")
        savePath = os.path.abspath("Stock Data/" + self.__exchangeCode + "/Sector Volatility Queries/" + inpDate)
        if os.path.exists(savePath) == False:
            os.makedirs(savePath)
        numMod = 1
        strMod = "(1)"
        if isfile(savePath + "/" + inpDate + ".txt") == True:
            while isfile(savePath + "/" + inpDate + strMod + ".txt"):
                numMod += 1
                strMod = "(" + str(numMod) + ")"
        else:
            strMod = ""
        newFile = open(savePath + "/" + inpDate + strMod + ".txt", "w")
        newFile.write(fileText)
        newFile.close()
        with open(savePath + "/" + inpDate + strMod + ".json", "w") as outfile:
            json.dump(jsonDict, outfile)
        

def update_sheets(exchangeCode, startCode):
    testSystem = stockSystem([], exchangeCode)
    testSystem.update_stock_spreadsheets(True, startCode)


#def stock_select_1(inpDate):


def create_daily_pickings(exchange, inpDate):
    testSystem = stockSystem([], exchange.upper())
    testSystem.init_stock_objects(inpDate)
    testSystem.load_stock_charts(inpDate)
    testSystem.add_stock_info(inpDate)
    result = testSystem.SD_test_func(5, 20)
    tempList = []
    for x in result:
        print(x)
        tempList.append(x[0])
    testSystem.create_daily_pickings(result, False, inpDate)

##RSSRetList = testSystem.RSS_check_for_keywords(tempList, ["new", "analyst", "rating"], 3)

##codeList = testSystem.check_for_crossover(RSSRetList, 5)


##testSystem = stockSystem([], "NASDAQ")
##testSystem.init_stock_objects("2016-05-15")#inpDate)
##testSystem.add_stock_info("2016-05-15")
##testSystem.print_stocks_in_similar_sector("NTAP")


def RSS_check(codeList):
    testSystem.add_RSS_stocks(codeList)
    testSystem.init_stocks_RSS()
    testSystem.RSS_search_feeds_loop()

def RSS_keyword_search(keywords, requiredNum):
    testSystem = stockSystem([], "LON")
    testSystem.init_stock_objects("2016-05-05")
    testSystem.load_stock_charts("2016-05-05")
    RSSRetList = testSystem.RSS_check_for_keywords(True, keywords, requiredNum)
    codeList = testSystem.check_for_crossover(RSSRetList, 3)

def volatility_search(inpExchange, inpDate, previous):
    testSystem = stockSystem([], inpExchange)
    testSystem.init_stock_objects(inpDate)
    testSystem.load_stock_charts(inpDate)
    testSystem.add_stock_info(inpDate)
    testSystem.volatility_search(previous, inpDate)


def sector_search_return(inpExchange, inpDate, superSector, sector, subSector, echo, openBrowser):
    testSystem = stockSystem([], inpExchange)
    testSystem.init_stock_objects(inpDate)
    testSystem.add_stock_info(inpDate)
    testSystem.sector_dict_search(superSector, sector, subSector, echo, openBrowser)


##volatility_search("LON", "2016-05-05")

##sector_search_return("LON", "2016-05-14",
##                     'real estate', 'real estate investment trusts', 'residential reits'
##                     , True, True)
    
##
##for itemCounter in range(len(actual)):
##    print actual[itemCounter]
##    print changes[itemCounter]
##    print ""

##testSystem.print_stocks_in_similar_sector("IEH")
    
##
##for item in ["IOF", "GKP", "PFG", "BOR", "GRPH", "AFC", "SQZ", "CWK", "MTC", "FQM", "KMR", "CHAR", "MAB1", "RNO", "HAWK", "ELA", "LMI", "ENQ", "HOC", "BPC"]:
##    testSystem.temp_func(item)

##stock_select_1("2016-05-07")

####update_sheets("LON", False)
##create_daily_pickings("LON", "2016-05-21")
##update_sheets("NYSE", False)
##create_daily_pickings("NYSE", "2016-05-19")
##update_sheets("AMEX", False)
##create_daily_pickings("AMEX", "2016-05-19")

##RSS_keyword_search(["new", "analyst", "rating"], 3)

##volatility_search("LON", "2016-05-05", 5)






#Useful sites
#http://www.stockmarketwire.com/




#Currently watching, 09/05/2016 before opening
#AVON - ?
#AFC - short?
#CWR - short?
#GRPH - short?
#PVCS - invest when increase starts again
#ITM - ?

#Currently watching, 14/05/2016 weekend Friday Night
#Shorting these stocks would have been completely the wrong call in the short run.
#Long run is yet to be seen
#HNR - ?

#15/05/2015
#KCR - real estate investment trust for london properties, interesting to watch,
#if my hunch is correct then at some point short it (bubble burst)
#PVCS prediction proving correct
#PVCS - short around Tues or Weds
#VLC - invest?

#TODO Idea: Every day make a list of predictions for the stocks with the top 20
#normalised deviations
#
#BUG: AAAP, DRIP, EDGE, UCP returned in SD_test
#LON:AVGR result but AEGR suggested
#
#America stock exchange functionality added: will focus from now on
#use robin hood app to make 25k capital for lightspeed viable?
#
#Is a period of 10 days better for taking the normalised SD, as it makes it more likely
#the stock will continue to go up and down?












