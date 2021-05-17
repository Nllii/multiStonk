#this one should simply look at the goodBuy list generated by an algo, and display the date added and % change since adding (essentially the same as what stonk2 was doing with fda)

import otherfxns as o
import sys,json,time,os
import datetime as dt
from colorama import init as colorinit

colorinit() #allow coloring in Windows terminals

#change display text color
class bcolor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



cfgFile = './configs/dryrun.config'

c = o.configparser.ConfigParser()
c.read(cfgFile)

sys.path.append(c['file locations']['stockAlgosDir'])


if(len(sys.argv)>1): #if there's an argument present
  if(len(sys.argv)<3):
    algo = sys.argv[1].lower()
  else:
    raise ValueError("Too many arguments. Please specify only one algo to test")
else: #no argument present
  raise ValueError("No argument present. Please specify the algo to test")
  

exec(f"import {algo}")
exec(f"{algo}.init('{cfgFile}')")

#TODO: figure out how scoring should work. Right now it's not effective at all
while True:
  todayList = eval(f"{algo}.getList()") #get today's list
  
  #get the cumulative list history (contains "purchase" date, symb, note, maxGain, maxLoss)
  if(os.path.isfile(c['file locations']['purchList'])): #if file exists
    purchList = json.loads(open(c['file locations']['purchList'],'r').read()) #read from the file
  else: #file doesn't exist
    purchList = {} #init with nothing
  #append today onto the cumulative and save to file
  for e in todayList:
    purchList[e] = {
      "purchDate":str(dt.date.today()),
      "buyPrice":0,
      "note":todayList[e],
      "high":1,
      "highDate":str(dt.date.today()),
      "low":1,
      "lowDate":str(dt.date.today())
    }
  
  prices = o.getPrices([e+"|stocks" for e in purchList]) #get prices for all stocks in the list
  prices = {s.split("|")[0]:prices[s]['price'] for s in prices} #isolate to {symb:price}
  
  #this way we only have to call getPrices once
  #go through all recorded ones (including today's), skip the ones already initiated, keep the ones present and in the price range, and remove the rest
  for e in list(purchList):
    if(purchList[e]['buyPrice']==0):
      if(e in prices):
        purchList[e]['buyPrice'] = prices[e]
      else:
        purchList.pop(e)
  
  print(f'testing algo "{algo}"')
  print("symb\tcurrent\thigh\thighDate\tlow\tlowDate\t\tnote")
  print("----\t-------\t-----\t----------\t-----\t----------\t----------")
  for e in purchList:
    if(e in prices):
      if(prices[e]/purchList[e]['buyPrice']>purchList[e]['high']):
        purchList[e]['high'] = round(prices[e]/purchList[e]['buyPrice'],2)
        purchList[e]['highDate'] = str(dt.date.today())
      elif(prices[e]/purchList[e]['buyPrice']<purchList[e]['low']):
        purchList[e]['low'] = round(prices[e]/purchList[e]['buyPrice'],2)
        purchList[e]['lowDate'] = str(dt.date.today())
    else:
      purchList[e]['note'] = "Delisted"
    
    print((f"{e}\t"
          f"{bcolor.FAIL if prices[e]/purchList[e]['buyPrice']<1 else bcolor.OKGREEN}{round(prices[e]/purchList[e]['buyPrice'],2)}{bcolor.ENDC}\t"
          f"{bcolor.FAIL if purchList[e]['high']<1 else bcolor.OKGREEN}{purchList[e]['high']}{bcolor.ENDC}\t"
          f"{purchList[e]['highDate']}\t"
          f"{bcolor.FAIL if purchList[e]['low']<1 else bcolor.OKGREEN}{purchList[e]['low']}{bcolor.ENDC}\t"
          f"{purchList[e]['lowDate']}\t"
          f"{purchList[e]['note']}"))
      
  
  open(c['file locations']['purchList'],'w').write(json.dumps(purchList)) #save to the file


  #display the list
  
  
  
  time.sleep(86400) #check once a day