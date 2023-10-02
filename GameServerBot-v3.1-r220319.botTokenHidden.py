import fs.fs as fs
import asyncio, discord
import random, time, pickle
import subprocess
import concurrent.futures
import os

'''
def integrateAsList(target):
    list = ['', '']
    commaExist = 0
    for count in range(1,len(target)-1):
        if commaExist == 0:
            if target[count] != ',':
                list[0] = list[0] + target[count]
            else:
                commaExist = 1
                continue
        elif commaExist == 1:
            commaExist = 2
            continue
        elif commaExist == 2:
            list[1] = list[1] + target[count]

    list[1] = list[1][1:-1] #따옴표 제거
    return list
'''
'''
def importUser(filePath):
    user = fs.read(filePath, "utf-8") #유저 정보 불러오기
    user = user.split(',')
    user[0] = user[0][2:-1]
    user[1] = user[1][2:-2]
    return user
'''
class customError(Exception): pass

class PredictEntry():
    def __init__(self, entryName):
        self.title = entryName
        self.entry = {}
        self.moneyTotal = 0

    def refresh(self):
        if self.entry == {}:
            self.moneyTotal = 0
            return
        total = 0
        for key in list(self.entry.keys()): total = total + self.entry[key]
        self.moneyTotal = total

    def append(self, username, money):
        if username in list(self.entry.keys()):
            self.entry[username] = self.entry[username] + money
        else:
            self.entry[username] = money
        self.refresh()

        
class Predict():

    def __init__(self, title): 
        self.title = title
        self.entry = []
        self.status = 0
        self.moneyTotal = 0

    def appendEntry(self, newEntryTitle):
        self.entry.append(PredictEntry(newEntryTitle))

    def addEntry(self, index, username, money):
        self.entry[index].append(username, money)
        self.refresh()

    def saveState(self):
        f = open("predictStatus.txt", 'wb')
        print("--Debug : saveState() called :", self.title, len(self.entry), self.status, self.moneyTotal)
        pickle.dump(self, f)
        f.close()

    def recallState(self):
        f = open("predictStatus.txt", 'rb')
        p = pickle.load(f)
        print("--Debug : recallState() called :", p.title, len(p.entry), p.status, p.moneyTotal)
        return p

    def refresh(self):
        if len(self.entry) == 0:
            self.moneyTotal = 0
            return
        total = 0
        for ct in range(len(self.entry)):
            total = total + self.entry[ct].moneyTotal
        self.moneyTotal = total
        print("--Debug : refresh() called : self.moneyTotal =", self.moneyTotal)

    def makeEmbed(self):
        #예측 임베드 출력
        self.refresh()
        if self.status == 0: description = "예측이 아직 시작되지 않았습니다."
        elif self.status == 1: description = "`$예측참여 <예측번호> <금액>` 을 입력하여 참여할 수 있습니다."
        elif self.status == 2: description = "현재 예측 참여가 종료되었습니다."
            
        description = description + "\n현재 총 적립 금액 {}원.".format(self.moneyTotal)

        embed = discord.Embed(title = "예측 : {}".format(self.title), description = description) #Embed 출력
        for ct in range(len(self.entry)):
            winratio = 0 if self.entry[ct].moneyTotal == 0 else self.moneyTotal / self.entry[ct].moneyTotal
            embed.add_field(name = "{}. {}".format(ct+1, self.entry[ct].title), value = "총 적립 금액 {}원 / 성공 배율 1 : {:.3f}".format(self.entry[ct].moneyTotal, winratio, inline = False))
        return embed


def setMoney(target, newMoneyValue):
    filePath = ".\dataMoney\{}.txt".format(target)
    fs.write(filePath, str(newMoneyValue))

def getMoney(target):
    filePath = ".\dataMoney\{}.txt".format(target)
    return int(fs.read(filePath))

def giveMoney(target, giveMoneyValue):
    filePath = ".\dataMoney\{}.txt".format(target)
    newMoneyValue = int(fs.read(filePath)) + giveMoneyValue
    fs.write(filePath, str(newMoneyValue))

def giveCoin(target, coinType, giveCoinValue):
    fs.write(".\dataCoin\{}\{}.txt".format(coinType, target), str(int(fs.read(".\dataCoin\{}\{}.txt".format(coinType, target))) + giveCoinValue))

def getCoin(target, coinType):
    coinList = fs.read(".\dataCoin\_coinList.txt", encoding='euc-kr').split('\r\n') #_coinList 불러오기
    if coinType not in coinList:
        raise customError
    filePath = ".\dataCoin\{}\{}.txt".format(coinType, target)
    if fs.exists(filePath) == False: #파일이 없다면 생성, 있다면 넘어가기
        fs.write(filePath, "0")

    return int(fs.read(".\dataCoin\{}\{}.txt".format(coinType, target)))

def getLottoEntries(inNumOrList):
    entries = fs.read(".\dataLotto\entries.txt")
    if entries == "":
        if inNumOrList == 'num': return 0
        elif inNumOrList == 'list': return []
        else: return 0
    else:
        entries = "none\n" + entries
        entries = entries.split('\n')
        entries.remove('none')
        if inNumOrList == 'num': return len(entries)
        elif inNumOrList == 'list': return entries
        else: return 0

def addAchievement(target, newAchievement):
    filePath = ".\dataAchievement\_alreadyAchieved\{}.txt".format(target)
    if fs.exists(filePath) == False: #파일이 없다면 생성
            fs.write(filePath, 'none\nnone2')
    fs.write(filePath, "\n" + newAchievement, append = True)

def getAchievement(target):
    filePath = ".\dataAchievement\_alreadyAchieved\{}.txt".format(target)
    achievementList = fs.read(filePath).split('\n')
    return achievementList

def getPredictStatus(): return int(fs.read('predictStatus.txt'))

def setPredictStatus(value): fs.write('predictStatus.txt', value)

'''
def predictAnalyze(predictListMoney):
    output1 = []
    output2 = []
    grandTotal = 0
    for ct1 in range(len(predictListMoney)):
        sum = 0
        keyList = list(predictListMoney[ct1].keys())
        for ct2 in range(len(keyList)): sum = sum + predictListMoney[ct1][keyList[ct2]]
        output1.append(sum)
        grandTotal = grandTotal + sum
    output1.append(grandTotal)
    for ct1 in range(len(predictListMoney)):
        if output1[ct1] != 0:
            output2.append("%.2f", grandTotal / output1[ct1])
        else:
            output2.append("-")
    output = [output1, output2]
    return output
'''
'''
def savePredictValue(predictTitle, predictList, predictListMoney): #predictValue.txt를 참조할 것
    pass
'''
'''
def getPredictValue():
    rawData = fs.read('predictValue.txt').split('\n')

    if len(rawData[0]) == 13:
        rawData[0] = ''
    else:
        rawData[0] = rawData[0][13:]

    if len(rawData[1]) == 12:
        rawData[1] = []
    else:
        rawData[1] = rawData[0][12:].split(',')

    if len(rawData[2]) == 17:
        rawData[2] = []
    else:
        temp = rawData[2][17:].split(',')
'''

def SortReactions(reactions):
    for ct1 in range(len(reactions)-1):
        for ct2 in range(len(reactions)-1):
            if reactions[ct2].count < reactions[ct2+1].count:
                temp = reactions[ct2]
                reactions[ct2] = reactions[ct2+1]
                reactions[ct2+1] = temp
    return reactions

def GetNumEmoji():
    return ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

def GetValMaplist():
    return ["헤이븐", "바인드", "스플릿", "아이스박스", "브리즈", "프랙쳐", "로터스"]

intents = discord.Intents.default()
#intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("봇 프로그램 정상 시작됨.")
    predict = Predict('')
    predict.saveState()
    print("--Debug : predict data reseted successfully.")
    await client.change_presence(status=discord.Status.online, activity=discord.Game("게임서버 관리")) #봇의 상태메시지

@client.event
async def on_message(message):

    #id = "{}".format(message.author)

    if message.content == "$test": #감지 대상 메시지
        await message.channel.send("{} | {}님 안녕하세요. 현재 봇이 정상 작동 중입니다.".format(message.author, message.author.mention)) #<< 대상 메시지의 채널에 전송
        #await message.author.send("{} | {}, Hello-2.".format(message.author, message.author.mention)) #<< 대상 메시지의 전송자에게 DM

    if message.content[0:4] == "$등록 ": #감지 대상 메시지
        if(message.author.bot): raise customError() #무한반복 차단
        if(message.author.id == client.user.id): raise customError() #로그인한 봇으로 채팅 입력 방지

        userNickname = message.content[4:]

        filePath = '.\dataNickname\{}.txt'.format(message.author)

        #파일이 없다면 생성, 있다면 넘어가기
        if fs.exists(filePath) == False:
            fs.write(filePath, '')
       
        fs.write(filePath, userNickname) #유저 정보 저장

        userNickname = fs.read(filePath)
        await message.channel.send("등록이 정상 처리되었습니다.\n등록된 디스코드 닉네임 : {} | 자기소개 : {} 입니다.".format(message.author, userNickname))

    if message.content[0:4] == "$검색 ":
        if(message.author.bot): raise customError() #무한반복 차단
        if(message.author.id == client.user.id): raise customError() #로그인한 봇으로 채팅 입력 방지

        filePath = ".\dataNickname\{}.txt".format(message.content[4:])

        if fs.exists(filePath) == False:
            await message.channel.send("조회하신 유저가 존재하지 않습니다.")
        else: 
            userNickname = fs.read(filePath)
            await message.channel.send("{} : {}".format(message.content[4:], userNickname))

    if message.content == "$도움말" or message.content == "$": #감지 대상 메시지
        embed = discord.Embed(title = "발로란트 연습용 봇", description = "도움말 페이지") #Embed 출력
        subtitle = "'$' 또는 '$도움말' 명령어를 입력하여 이 창을 열 수 있습니다."
        embed.add_field(name = subtitle, value = fs.read("commands.txt", encoding = 'euc-kr'), inline = False)
        embed.add_field(name = "페이지 2", value = fs.read("commands2.txt", encoding = 'euc-kr'), inline = False)
        await message.channel.send(embed=embed)
        #await message.channel.send(fs.read("commands.txt", encoding = 'euc-kr'))

    if message.content == "$돈줘": #감지 대상 메시지
        if(message.author.bot): raise customError() #무한반복 차단
        if(message.author.id == client.user.id): raise customError() #로그인한 봇으로 채팅 입력 방지

        moneyAmountBase = int(fs.read(".\dataMoney\moneyAmount.txt")) #1번당 줄 돈
        moneyAmount = random.randint(0, 2*moneyAmountBase) #제공량 랜덤화
        giveMoney("moneyJackpot", 2 * moneyAmount) #잭팟 창고 적립
        if moneyAmount >= int(2 * moneyAmountBase): #이스터에그 : 낮은 확률로 잭팟
            moneyAmount = getMoney("moneyJackpot")
            setMoney("moneyJackpot", 0)
            await message.channel.send(">>> >> {}님 잭팟! 당첨금 : {}원 <<".format(message.author.mention, str(moneyAmount)))


        filePath = '.\dataMoney\{}.txt'.format(message.author)

        #파일이 없다면 생성, 있다면 넘어가기
        if fs.exists(filePath) == False:
            fs.write(filePath, "0")

        userMoney = int(fs.read(filePath)) + moneyAmount #돈 정보 불러오기 + 추가
        fs.write(filePath, str(userMoney)) #돈 정보 갱신
        await message.channel.send("{}원이 지급되었습니다. 현재 {}님의 잔고는 {}원입니다. // 현재 잭팟적립금은 총 {}원입니다.".format(str(moneyAmount), message.author.mention, str(userMoney), str(getMoney("moneyJackpot"))))

    if message.content[0:4] == "$도박 ": #감지 대상 메시지
        if(message.author.bot): raise customError() #무한반복 차단
        if(message.author.id == client.user.id): raise customError() #로그인한 봇으로 채팅 입력 방지

        filePath = '.\dataMoney\{}.txt'.format(message.author)

        #파일이 없다면 넘어가기
        if fs.exists(filePath) == False:
            await message.channel.send("{}님의 돈 데이터가 존재하지 않습니다. '$돈줘' 명령어를 사용해보세요.".format(message.author.mention))
            raise customError()
        
        userMoney = int(fs.read(filePath)) #돈 정보 불러오기
        gambleMoney = int(message.content[4:])
        if gambleMoney < 0: raise customError() #0원보다 작으면 무시

        if userMoney >= gambleMoney:
            dice = random.randint(0,1)
            if dice == 1:
                userMoney = userMoney + gambleMoney
                await message.channel.send("승리하여 {}원을 얻었습니다. 현재 {}님의 잔고는 {}원입니다.".format(str(gambleMoney), message.author.mention, str(userMoney)))
            else:
                userMoney = userMoney - gambleMoney
                await message.channel.send("패배하여 {}원을 잃었습니다. 현재 {}님의 잔고는 {}원입니다.".format(str(gambleMoney), message.author.mention, str(userMoney)))
        else:
            await message.channel.send("돈이 부족합니다. 현재 {}님의 잔고는 {}원입니다.".format(message.author.mention, str(userMoney)))

        fs.write(filePath, str(userMoney)) #돈 정보 갱신

    if message.content == "$복권": #감지 대상 메시지
        if(message.author.bot): raise customError() #무한반복 차단
        if(message.author.id == client.user.id): raise customError() #로그인한 봇으로 채팅 입력 방지

        await message.channel.send(fs.read("lottoInfo.txt", encoding = 'euc-kr'))
        entryfee = int(fs.read(".\dataLotto\entryfee.txt"))
        await message.channel.send("현재 복권의 구매자 수는 {}명입니다. 복권의 가격은 {}원이고, 총 당첨금은 {}원입니다.".format(getLottoEntries('num'), str(entryfee), str(getLottoEntries('num')*entryfee)))

    if message.content == "$내복권": #감지 대상 메시지
        if(message.author.bot): raise customError() #무한반복 차단
        if(message.author.id == client.user.id): raise customError() #로그인한 봇으로 채팅 입력 방지

        entries = getLottoEntries('list')
        await message.channel.send("현재 회차에서 {}님이 구매한 복권은 {}장입니다. 현재 당첨 확률은 {}/{}입니다.".format(message.author.mention, entries.count(str(message.author)), entries.count(str(message.author)), len(entries)))

    if message.content == "$복권구매": #감지 대상 메시지
        if(message.author.bot): raise customError() #무한반복 차단
        if(message.author.id == client.user.id): raise customError() #로그인한 봇으로 채팅 입력 방지

        entryfee = int(fs.read(".\dataLotto\entryfee.txt"))

        if fs.read(".\dataLotto\possibleToBuy.txt") == 'no': raise customError() #추첨시 구매 코드 비활성화

        if getMoney(message.author) < entryfee:
            await message.channel.send("복권을 구매할 돈이 부족합니다. 현재 {}님의 잔고는 {}원입니다.".format(message.author.mention, getMoney(message.author)))
        else:
            giveMoney(message.author, -1 * entryfee)
            if getLottoEntries('num') == 0:
                fs.write(".\dataLotto\entries.txt", str(message.author))
            else:
                fs.write(".\dataLotto\entries.txt", "\n" + str(message.author), append=True)
            
            entries = getLottoEntries('list')
            await message.channel.send("성공적으로 복권을 구매하셨습니다. 현재 회차에서 {}님이 구매한 복권은 {}장입니다. 현재 당첨 확률은 {}/{}입니다.".format(message.author.mention, entries.count(str(message.author)), entries.count(str(message.author)), len(entries)))
            
    if message.content == "$복권정산" and message.author.id == 597055775860326410: #나만 실행할 수 있다
        fs.write(".\dataLotto\possibleToBuy.txt", "no")
        await message.channel.send("복권을 추첨하는 중입니다... 약 5초 후 결과가 공개됩니다.")

        entries = getLottoEntries('list')
        winner = entries[random.randint(0, len(entries)-1)]
        entryfee = int(fs.read(".\dataLotto\entryfee.txt"))
        prize = entryfee * len(entries)

        time.sleep(5)
        giveMoney(winner, prize)
        await message.channel.send("복권 당첨자는 {}님 입니다! 당첨금 {}원이 지급돠었습니다!".format(winner, prize))

        fs.write(".\dataLotto\entries.txt", "") #초기화 페이즈
        fs.write(".\dataLotto\possibleToBuy.txt", "yes")

    if message.content == "$랭킹":
        rankLists = []
        players = list(fs.list(".\dataMoney"))
        players.remove(".\\dataMoney\\moneyAmount.txt") #기본 파일인 moneyAmount 제거
        players.remove(".\\dataMoney\\moneyJackpot.txt")
        for ct in range(0, len(players)):
            rankLists.append([players[ct][12:-4], getMoney(players[ct][12:-4])])
            ct2 = ct
            while rankLists[ct2][1] > rankLists[ct2-1][1]:
                temp = rankLists[ct2]
                rankLists[ct2] = rankLists[ct2-1]
                rankLists[ct2-1] = temp
                if ct2 == 1: break
                ct2 = ct2 -1

        embed = discord.Embed(title = "게임서버머니 랭킹", description = "1~10위") #Embed 출력
        rank1 = rankLists[0][0] + " - " + str(rankLists[0][1])
        rank2to10 = ""
        for ct in range (1,10):
            rank2to10 = rank2to10 + rankLists[ct][0] + " - " + str(rankLists[ct][1]) + "\n"
        embed.add_field(name = rank1, value = rank2to10, inline = False)
        await message.channel.send(embed=embed)

    if message.content[0:3] == "$송금":
        command = message.content[4:].split('=')
        money = int(command[1])
        target = command[0]
        user = str(message.author)

        if money < 0: raise customError() #0원보다 작으면 무시

        if getMoney(user) < money:
            await message.channel.send("송금할 돈이 부족합니다. 현재 {}님의 잔고는 {}원입니다.".format(user, getMoney(user)))
        else:
            giveMoney(target,money)
            giveMoney(user,-1 * money)
            
            await message.channel.send("성공적으로 송금되었습니다. {}님의 남은 잔고는 {}원입니다.".format(user, getMoney(user)))

    if message.content == "$코인":
        embed = discord.Embed(title = "현재 게임서버 코인 시세", description = "시세는 실시간으로 변동될 수 있음") #Embed 출력
        nameField = "$코인 명령어를 이용하여 코인의 실시간 시세를 조회할 수 있습니다."
        coinsInfo = "-----------------------------------------------------------------------------------------------\n"
        coinList = fs.read(".\dataCoin\_coinList.txt", encoding='euc-kr').split('\r\n') #_coinList 불러오기
        for ct in range(0, len(coinList)):
            coinsInfo = coinsInfo + '\n' + coinList[ct] + ' - ' + fs.read(".\dataCoin\{}\_coinValue.txt".format(coinList[ct])) + '원'

        embed.add_field(name = nameField, value = coinsInfo, inline = False)
        await message.channel.send(embed=embed)

    if message.content[0:5] == "$코인구매":
        command = message.content[6:].split(' ')
        coinType = command[0]
        coinQuantity = int(command[1])
        if coinQuantity < 0: raise customError() #0개보다 작으면 무시
        user = str(message.author)
        coinList = fs.read(".\dataCoin\_coinList.txt", encoding='euc-kr').split('\r\n') #_coinList 불러오기
        if coinType not in coinList:
            await message.channel.send("존재하지 않는 코인 이름입니다.")
            raise customError
        coinValue = int(fs.read(".\dataCoin\{}\_coinValue.txt".format(coinType)))
        filePath = ".\dataCoin\{}\{}.txt".format(coinType, user)        
        if fs.exists(filePath) == False: #파일이 없다면 생성, 있다면 넘어가기
            fs.write(filePath, "0")

        if getMoney(user) < coinQuantity * coinValue:
            await message.channel.send("돈이 부족합니다.")
        else:
            giveMoney(user, -1 * coinQuantity * coinValue)
            giveCoin(user, coinType, coinQuantity)
            await message.channel.send("성공적으로 개당 {}원에 구매되었습니다. 구매금은 {}원이고 남은 잔고는 {}원입니다.".format(coinValue, coinQuantity * coinValue, getMoney(user)))

    if message.content[0:5] == "$코인판매":
        command = message.content[6:].split(' ')
        coinType = command[0]
        coinQuantity = int(command[1])
        if coinQuantity < 0: raise customError() #0개보다 작으면 무시
        user = str(message.author)
        coinList = fs.read(".\dataCoin\_coinList.txt", encoding='euc-kr').split('\r\n') #_coinList 불러오기
        if coinType not in coinList:
            await message.channel.send("존재하지 않는 코인 이름입니다.")
            raise customError
        coinValue = int(fs.read(".\dataCoin\{}\_coinValue.txt".format(coinType)))
        filePath = ".\dataCoin\{}\{}.txt".format(coinType, user)
        if fs.exists(filePath) == False: #파일이 없다면 생성, 있다면 넘어가기
            fs.write(filePath, "0")

        if getCoin(user, coinType) < coinQuantity:
            await message.channel.send("보유 코인이 부족합니다.")
        else:
            giveCoin(user, coinType, -1 * coinQuantity)
            giveMoney(user, coinQuantity * coinValue)
            await message.channel.send("성공적으로 개당 {}원에 판매되었습니다. 판매금은 {}원이고 남은 잔고는 {}원입니다.".format(coinValue, coinQuantity * coinValue, getMoney(user)))

    if message.content == "$내코인":
        user = str(message.author)
        embed = discord.Embed(title = "{}님의 코인 보유 목록".format(user), description = "시세는 실시간으로 변동될 수 있음") #Embed 출력
        nameField = "$내코인 명령어를 이용하여 자신이 보유중인 코인 목록을 조회할 수 있습니다."
        coinsInfo = "-----------------------------------------------------------------------------------------------\n"
        coinList = fs.read(".\dataCoin\_coinList.txt", encoding='euc-kr').split('\r\n') #_coinList 불러오기
        for ct in range(0, len(coinList)):
            mycoin = getCoin(user, coinList[ct])
            coinValue = int(fs.read(".\dataCoin\{}\_coinValue.txt".format(coinList[ct])))
            coinsInfo = coinsInfo + '\n' + coinList[ct] + ' - {}개(시세 '.format(mycoin) + str(mycoin * coinValue)  + '원)'

        embed.add_field(name = nameField, value = coinsInfo, inline = False)
        await message.channel.send(embed=embed)



    if message.content[0:6] == "$예측호스트" and message.author.id == 597055775860326410: #나만 실행할 수 있다
        predict = Predict('')
        predict = predict.recallState()

        if predict.status != 0:
            await message.channel.send("이미 예측이 진행 중입니다!")
            raise customError

        predictList = message.content[7:].split(' / ')
        predict = Predict(predictList[0])
        del predictList[0]

        predict.status = 1
        
        for ct in range(len(predictList)):
            predict.appendEntry(predictList[ct])

        predict.saveState()
        print("--Debug : predict.status = ", predict.status)
                
        await message.channel.send(embed = predict.makeEmbed())

    if message.content == "$예측마감" and message.author.id == 597055775860326410: #나만 실행할 수 있다
        predict = Predict('')
        predict = predict.recallState()

        if predict.status == 0:
            await message.channel.send("예측이 아직 시작되지 않았습니다.")
            raise customError
        if predict.status == 2:
            await message.channel.send("이미 예측이 마감되었습니다.")
            raise customError
        
        predict.status = 2
        predict.saveState()
        await message.channel.send("예측이 마감되었습니다.")
        print("--Debug : predict.status =", predict.status)

    if message.content == "$예측":
        predict = Predict('')
        predict = predict.recallState()
        if predict.status == 1 or predict.status == 2:
            await message.channel.send(embed = predict.makeEmbed())

        elif predict.status == 0:
            await message.channel.send("현재 진행 중인 예측이 없습니다.")

    if message.content[0:6] == "$예측참여 ":
        predict = Predict('')
        predict = predict.recallState()

        user = str(message.author)
        if predict.status == 0:
            await message.channel.send("예측이 아직 시작되지 않았습니다.")
            raise customError
        if predict.status == 2:
            await message.channel.send("이미 예측이 마감되었습니다.")
            raise customError
        predictInput = message.content.split()
        if int(predictInput[2]) > getMoney(user):
            await message.channel.send("돈이 부족합니다.")
            raise customError
        if int(predictInput[2]) < 0:
            await message.channel.send("0원 이상을 입력해주세요.")
            raise customError
        if int(predictInput[1]) <= 0 or int(predictInput[1]) > len(predict.entry):
            await message.channel.send("잘못된 인덱스입니다.")
            raise customError

        giveMoney(user, -1 * int(predictInput[2]))
        predict.addEntry(int(predictInput[1])-1, user, int(predictInput[2]))
        predict.saveState()
        
        await message.channel.send("{}원이 {}번 예측 항목에 정상적으로 적립되었습니다.".format(predictInput[2], predictInput[1]))

    if message.content[0:5] == "$예측정산" and message.author.id == 597055775860326410: #나만 실행할 수 있다
        predict = Predict('')
        predict = predict.recallState()

        predictInput = message.content.split()
        target = int(predictInput[1])
        print("--Debug : predict.moneyTotal =", predict.moneyTotal, "/ predict.entry[target-1].moneytotal =", predict.entry[target-1].moneyTotal)
        if target < 0 or int(predictInput[1]) > len(predict.entry):
            await message.channel.send("잘못된 인덱스입니다.")
            raise customError
        elif target == 0:
            for ct in range(len(predict.entry)):
                targetEntry = predict.entry[ct]
                users = list(targetEntry.keys())
                for ct2 in range(users):
                    giveMoney(users[ct2], targetEntry[users[ct2]])
            await message.channel.send("예측이 취소되었습니다.")

        else:            
            winratio =  predict.moneyTotal / predict.entry[target-1].moneyTotal if predict.entry[target-1].moneyTotal != 0 else 0
                       
            targetEntry = predict.entry[target-1].entry
            for ct in range(len(list(targetEntry.keys()))):
                user = list(targetEntry.keys())[ct]
                winmoney = int(targetEntry[user] * winratio)
                giveMoney(user, winmoney)
                await message.channel.send("{}에게 {}원이 지급되었습니다!(원래 적립 금액 : {}원)".format(user, winmoney, targetEntry[user]))
                
            embed = predict.makeEmbed()
            embed.add_field(name = "정답은 {}번이었습니다!".format(target), value = "{}번 항목에 적립된 금액 총 {}원이 {:.3f}배로 불어났습니다! 축하합니다!".format(target, predict.entry[target-1].moneyTotal, winratio), inline = False)
            
            await message.channel.send(embed=embed)
            
        predict = Predict('')
        predict.saveState()
        print("--Debug : predict.status = ", predict.status)

    if message.content == "$admin_resetpredict" and message.author.id == 597055775860326410: #나만 실행할 수 있다
        predict = Predict('')
        predict.saveState()
        await message.channel.send("Predict data reseted successfully.")

    if message.content == "$내전맵투표":
        await message.channel.send('"$내전맵투표 <투표시간(초)>" 의 형태로 입력해주세요.')

    if message.content[0:6] == "$내전맵투표" and message.author.bot == False:
        timedelay = int(message.content[7:])
        embed = discord.Embed(title = "내전 맵 투표", description = "원하는 맵에 해당하는 반응 이모지를 눌러주세요.")
        numEmoji = GetNumEmoji()
        valMapList = GetValMaplist()
        for ct in range(1,8):
            embed.add_field(name = "", value =  numEmoji[ct] + valMapList[ct-1], inline = False)

        await message.channel.send(content = "내전 맵 투표를 시작합니다. 투표 시간 : {}초".format(timedelay), embed = embed)
        #await message.channel.send("$내전맵투표 활성화 - 내전 맵 투표를 시작합니다. \n\n:one:헤이븐 // :two:바인드 // :three:스플릿 // :four:아이스박스 // :five:브리즈 // :six:프랙쳐 // :seven:로터스 \n\n투표 시간 : {}초".format(timedelay))  

    if message.content[0:7] == "내전 맵 투표" and message.author.bot == True:
        numEmoji = GetNumEmoji()
        for ct in range(1,8):
            await message.add_reaction(numEmoji[ct])
        temp = str(message.content).split(" : ")
        timedelay = int(temp[-1][0:-1])
        time.sleep(timedelay)
        embed = discord.Embed(title = "투표가 종료되었습니다!", description = "투표 결과 (봇의 기본 설정 투표 제외)")

        reactions = message.reactions
        sortedReactions = SortReactions(reactions)

        rank = 0
        while sortedReactions != []:
            rank = rank + 1
            rankName = str(rank) + "위"
            rankCount = sortedReactions[0].count
            rankEmoji = ""
            while sortedReactions != [] and sortedReactions[0].count == rankCount:
                rankEmoji = rankEmoji + sortedReactions[0].emoji + " "
                del sortedReactions[0]
            embed.add_field(name = rankName, value = rankEmoji + str(rankCount-1) + "표", inline = False)

        #for ct in range(len(sortedReactions)):
        #    emoji = sortedReactions[ct].emoji
        #    embed.add_field(name = "{}위".format(ct+1), value = "{} {} {}표".format(emoji, emoji[1:-1], sortedReactions[ct].count-1), inline = False)

        await message.channel.send(embed=embed)


'''
    if message.content == "봇, 내 소개를 부탁해!": #감지 대상 메시지
        await message.channel.send("""
--------------------------------------------------------------------------------------------

보카Bokha_#7287 05년생 18세 남자
발로닉 - GMS 망토단 보카#Bokha(플레 2) / GMS 망토단 보카#0221(플레 2) / GMS 가디언맨#0221(언랭)
발로 실력 - 그날그날에 따라 브론즈급 ~ 다이아몬드급
주무기 - 벤달과 *오딘*

저의 정신세계 깊은 곳에는 여러분들이 모르는 이면이 있습니다
아무도 내 머릿속을 알 수 없으셈 ㅋㅋ
고등학교에서 전교권을 맡고있는 보카입니다 감사합니다(~제리인사)

--------------------------------------------------------------------------------------------
""") #<< 대상 메시지의 채널에 전송
'''

env = os.environ
print(env['PATH']) 


#client.run(fs.read(".\\botToken.txt"))