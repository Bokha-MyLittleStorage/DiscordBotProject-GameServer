from random import randint
from time import sleep
import math
import fs

def coinRefresh():
    coinList = fs.read(".\dataCoin\_coinList.txt", encoding='euc-kr').split('\r\n')
    print(coinList)
    coinList.remove('STABLEcoin')
    for ct in range(0, len(coinList)):
        filePath = ".\dataCoin\{}\_coinValue.txt".format(coinList[ct])
        originValue = int(fs.read(filePath))
        newValue = int(originValue * math.exp(0.0001 * randint(-303, 300)))
        fs.write(filePath, str(newValue))

refreshCount = 0
while True: 
    sleep(int(fs.read("coinChangeInterval.txt")))
    coinRefresh()
    refreshCount = refreshCount+1
    print("refreshed = {}".format(refreshCount))
 