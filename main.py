import json, websocket, ssl, os, random

shit = 0

class UNO:

    def __init__(self):
        self.cardList = []
        self.playerCardList = []
        self.playerList = []
        self.gameStatus = 0
        self.firstMan = ''
        self.firstCard = ''

    def initialize_card(self):
        self.cardList = []
        for j in '红黄蓝绿':
            for i in range(1, 10):
                self.cardList.append(j + str(i))
                self.cardList.append(j + str(i))
            for i in ['+2', '禁', '转向']:
                self.cardList.append(j + i)
                self.cardList.append(j + i)
            self.cardList.append(j + '0')
        for i in range(4):
            self.cardList.append('+4')
            self.cardList.append('变色')
        print(f'已初始化{len(self.cardList)}张：{self.cardList}')

    def no_card(self, num):
        if len(self.cardList) < num:
            self.cardList = self.initialize_card()
            for i in self.playerCardList:
                for j in i:
                    self.cardList.remove(j)
            chat.sendMsg('牌没了，已重新洗牌。')

    def start_game(self):
        self.gameStatus = 1
        self.initialize_card()
        for i in range(len(self.playerList)):
            playerCard = []
            for j in range(7):
                addCard = random.choice(self.cardList)
                playerCard.append(addCard)
                self.cardList.remove(addCard)
            self.playerCardList.append(playerCard)
        self.firstMan = random.choice(self.playerList)
        self.firstCard = random.choice(self.cardList)
        while self.firstCard == '+4':
            self.firstCard = random.choice(self.cardList)
        self.cardList.remove(self.firstCard)

    def stop_game(self):
        self.gameStatus = 0
        self.playerList = []
        self.playerCardList = []

    def pass_(self, id, sender):
        nextId = (id + 1) % len(self.playerList)
        addCard = random.choice(self.cardList)
        self.cardList.remove(addCard)
        if addCard[1:] == '禁':
            self.ban(id)
            chat.sendMsg(f'`{sender}`补到了=={addCard}==并将其打出，`{self.playerList[nextId]}`跳过1轮，轮到`{self.firstMan}`！')
        elif addCard[1:] == '+2':
            self.add2(id)
            chat.sendMsg(f'`{sender}`补到了=={addCard}==并将其打出，`{self.playerList[nextId]}`加2张，轮到`{self.firstMan}`！')
            chat.sendTo(self.playerList[nextId], f'你新增了2张牌，这是你现在的牌：{self.playerCardList[nextId]}。')
        elif addCard[1:] == '转向':
            self.turn(id)
            chat.sendMsg(f'`{sender}`补到了{addCard}并将其打出，==顺序转换==，轮到`{self.firstMan}`！')
        else:
            self.firstMan = self.playerList[nextId]
            self.playerCardList[id].append(addCard)
            chat.sendMsg(f'`{sender}`补了一张牌，轮到`{self.firstMan}`！')
            chat.sendTo(sender, f'你新增了1张牌，这是你现在的牌：{ self.playerCardList[id]}。')

    def add4(self, color, id):
        nextId = (id + 1) % len(self.playerList)
        next2Id = (id + 2) % len(self.playerList)
        self.no_card(4)
        self.firstCard = color + '?'
        self.firstMan = self.playerList[next2Id]
        for i in range(4):
            addCard = random.choice(self.cardList)
            self.playerCardList[nextId].append(addCard)
            self.cardList.remove(addCard)

    def color(self, color, id):
        nextId = (id + 1) % len(self.playerList)
        self.firstMan = self.playerList[nextId]
        self.firstCard = color + '?'

    def ban(self, id):
        next2Id = (id + 2) % len(self.playerList)
        self.firstMan = self.playerList[next2Id]

    def add2(self, id):
        nextId = (id + 1) % len(self.playerList)
        next2Id = (id + 2) % len(self.playerList)
        self.firstMan = self.playerList[next2Id]
        self.no_card(2)
        for i in range(2):
            addCard = random.choice(self.cardList)
            self.playerCardList[nextId].append(addCard)
            self.cardList.remove(addCard)

    def turn(self, id):
        global shit
        shit = 1
        self.playerList.reverse()
        self.playerCardList.reverse()
        self.firstMan = self.playerList[(-id) % len(self.playerList)]
            

class HackChat:

    def __init__(self, channel: str, nick: str, passwd: str):
        self.channel = channel
        self.nick = nick
        self.passwd = passwd
        self.ws = websocket.create_connection(
            "wss://hack.chat/chat-ws", sslopt={"cert_reqs": ssl.CERT_NONE})
        self._sendPacket({
            "cmd": "join",
            "channel": channel,
            "nick": nick + "#" + passwd
        })
        self.onlineUsers = []

    def sendTo(self, nick, msg: str):
        self._sendPacket({
            "cmd": "whisper",
            "nick": nick,
            "text": msg,
        })

    def sendMsg(self, msg: str):
        self._sendPacket({
            "cmd": "chat",
            "text": msg,
        })

    def _sendPacket(self, packet: dict):
        encoded = json.dumps(packet)
        self.ws.send(encoded)

    def onJoin(self, joiner, hash, trip):
        self.onlineUsers.append(joiner)

    def onLeave(self, lefter):
        self.onlineUsers.remove(lefter)

    def onSet(self, nicks, result):
        self.onlineUsers = nicks

    def onWhisper(self, sender, msg):
        if sender == self.nick: return
        print(f"{sender}悄悄说：{msg}")

    def onMessage(self, sender, msg, trip):
        global shit
        print(f"{sender}：{msg}")
        if sender == self.nick: return
            
        if msg == 'uno':
            if uno.gameStatus:
                self.sendMsg('游戏已经开始了，等下一轮吧。')
                return 0
            if sender in uno.playerList:
                self.sendMsg('你已经加入了！')
            else:
                uno.playerList.append(sender)
                self.sendMsg(f'加入成功，现在有{len(uno.playerList)}人。')
                
        if (msg == '开始u' or len(uno.playerList) == 8) and not uno.gameStatus:
            if len(uno.playerList) >= 2:
                if len(uno.playerList) == 8:
                    self.sendMsg('人数达到上限，游戏自动开始！')
                uno.start_game()
                for i in range(len(uno.playerCardList)):
                    self.sendTo(uno.playerList[i],
                                f'这是你的牌：{uno.playerCardList[i]}')
                self.sendMsg(
                    f'牌发完啦，初始牌是=={uno.firstCard}==，请`{uno.firstMan}`先出！')
            else:
                self.sendMsg('人数不够！')
                
        if msg == '结束u' and uno.gameStatus:
            uno.stop_game()
            self.sendMsg('结束了...')
            
        if msg[:2] == 'u ' and sender == uno.firstMan:
            msgList = msg.split()
            card = msgList[1]
            id = uno.playerList.index(sender)
            nextId = (id + 1) % len(uno.playerList)
            next2Id = (id + 2) % len(uno.playerList)
            if card == 'check':
                self.sendTo(
                    sender,
                    f'现在牌面上的牌是=={uno.firstCard}==，这是你的牌：{uno.playerCardList[id]}')
                return 0
                
            if card == '.':
                uno.pass_(id, sender)
                return 0
                
            if card not in uno.playerCardList[id]:
                self.sendMsg('你没有那张牌！')
                return 0
                
            if card == '+4':
                for i in uno.playerCardList[id]:
                    if i[0] == uno.firstCard[0]:
                        self.sendMsg('不符合规则！')
                        return 0
                if len(msgList) < 3:
                    self.sendMsg('缺少参数！')
                    return 0
                if msgList[2] not in '红黄蓝绿':
                    self.sendMsg('参数错误！')
                    return 0
                uno.add4(msgList[2], id)
                self.sendMsg(
                    f'`{sender}`出了+4（王牌），`{uno.playerList[nextId]}`加四张，颜色变为=={msgList[2]}==，轮到`{uno.firstMan}`！'
                )
                self.sendTo(uno.playerList[nextId],
                            f'你新增了4张牌，这是你现在的牌：{ uno.playerCardList[nextId]}。')
                
            if card == '变色':
                if len(msgList) < 3:
                    self.sendMsg('缺少参数！')
                    return 0
                if msgList[2] not in '红黄蓝绿':
                    self.sendMsg('参数错误！')
                    return 0
                uno.color(msgList[2], id)
                self.sendMsg(
                    f'`{sender}`出了变色牌，颜色变为=={msgList[2]}==，轮到`{uno.firstMan}`！')
            
            if card[0] == uno.firstCard[0] or card[1:] == uno.firstCard[
                    1:] or uno.firstCard == '变色':
                uno.firstCard = card
                if card[1:] == '禁':
                    uno.ban(id)
                    self.sendMsg(
                        f'`{sender}`出了=={card}==，`{uno.playerList[nextId]}`跳过1轮，轮到`{uno.firstMan}`！'
                    )
                elif card[1:] == '+2':
                    uno.add2(id)
                    self.sendMsg(
                        f'`{sender}`出了=={card}==，`{uno.playerList[nextId]}`加2张，轮到`{uno.firstMan}`！'
                    )
                    self.sendTo(uno.playerList[nextId],
                                f'你新增了2张牌，这是你现在的牌：{uno.playerCardList[nextId]}。')
                elif card[1:] == '转向':
                    uno.turn(id)
                    self.sendMsg(
                        f'`{sender}`出了{card}，==顺序转换==，轮到`{uno.firstMan}`！')
                else:
                    uno.firstMan = uno.playerList[nextId]
                    self.sendMsg(f'`{sender}`出了=={card}==，轮到`{uno.firstMan}`！')
            elif card not in ['+4', '变色']:
                self.sendMsg('不符合规则！')
                return 0
            if shit:
                id = ( - id - 1) % len(uno.playerList)
                shit = 0
            uno.playerCardList[id].remove(card)
            if len(uno.playerCardList[id]) == 1:
                self.sendMsg(f'`{sender}`==UNO==了！！！')
            if len(uno.playerCardList[id]) == 0:
                self.sendMsg(f'`{sender}`获胜，游戏结束。')
                uno.stop_game()
                return 0
            uno.no_card(1)

    def run(self):
        while True:
            result = json.loads(self.ws.recv())
            cmd = result["cmd"]
            rnick = result.get("nick")
            if cmd == "chat":
                self.onMessage(rnick, result["text"], result.get("trip"))
            elif cmd == "onlineAdd":
                self.onJoin(rnick, result["hash"], result.get("trip"))
            elif cmd == "onlineRemove":
                self.onLeave(rnick)
            elif result.get("type") == "whisper":
                self.onWhisper(result["from"],
                               "".join(result["text"].split(": ")[1:]))
            elif cmd == "onlineSet":
                self.onSet(result["nicks"], result)
            elif cmd == "warn":
                print(result["text"])


if __name__ == '__main__':
    chat = HackChat("lounge", "Mr_UNO", os.getenv("pswd"))
    uno = UNO()
    chat.run()
