import json, websocket, ssl, os, random
cardList = []
playerList = []
playerCardList = []
gameStatus = False
firstMan, firstCard = '', '+4'
def initialize_card():
  cardList = []
  for j in '红黄蓝绿':
    for i in range(1, 10):
      cardList.append(j + str(i))
      cardList.append(j + str(i))
    for i in ['+2', '禁', '转向']:
      cardList.append(j + i)
      cardList.append(j + i)
    cardList.append(j + '0')
  for i in range(4):
    cardList.append('+4')
    cardList.append('变色')
  print(f'已初始化{len(cardList)}张：{cardList}')
  return cardList

  
class HackChat:
  def __init__(self, channel: str, nick: str, passwd: str):
    self.channel = channel
    self.nick = nick
    self.passwd = passwd
    self.ws = websocket.create_connection("wss://hack.chat/chat-ws",
                                          sslopt={"cert_reqs": ssl.CERT_NONE})
    self._sendPacket({
      "cmd": "join",
      "channel": channel,
      "nick": nick + "#" + passwd
    })
    self.onlineUsers = []

  def sendTo(self, nick, msg:str):
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
    global playerList, playerCardList, gameStatus, firstMan, firstCard, cardList
    print(f"{sender}：{msg}")
    if sender == self.nick: return
    if msg == 'uno':
      if gameStatus:
        self.sendMsg('游戏已经开始了，等下一轮吧。')
        return 0
      if sender in playerList:
        self.sendMsg('你已经加入了！')
      else:
        playerList.append(sender)
        self.sendMsg(f'加入成功，现在有{len(playerList)}人。')
    if msg == '开始u' and not gameStatus:
      if len(playerList) >= 2:
        gameStatus = True
        cardList = initialize_card()
        for i in range(len(playerList)):
          playerCard = []
          for j in range(7):
            addCard = random.choice(cardList)
            playerCard.append(addCard)
            cardList.remove(addCard)
          playerCardList.append(playerCard)
          self.sendTo(playerList[i], f'这是你的牌：{playerCard}')
        firstMan = random.choice(playerList)
        while firstCard == '+4':
          firstCard = random.choice(cardList)
        cardList.remove(firstCard)
        self.sendMsg(f'牌发完啦，初始牌是=={firstCard}==，请`{firstMan}`先出！')
      else:
        self.sendMsg('人数不够！')
    if msg == '结束u' and gameStatus:
      gameStatus = False
      playerList = []
      playerCardList = []
      self.sendMsg('结束了...')
    if msg[:2] == 'u ' and sender == firstMan:
      msgList = msg.split()
      card = msgList[1]
      id = playerList.index(sender)
      nextId = (id + 1) % len(playerList)
      next2Id = (id + 2) % len(playerList)
      if card == 'check':
        self.sendTo(sender, f'现在牌面上的牌是=={firstCard}==，这是你的牌：{playerCardList[id]}')
        return 0
      if card == '.':
        firstMan = playerList[nextId]
        addCard = random.choice(cardList)
        playerCardList[id].append(addCard)
        cardList.remove(addCard)
        self.sendMsg(f'`{sender}`补了一张牌，轮到`{firstMan}`！')
        self.sendTo(sender, f'你新增了1张牌，这是你现在的牌：{ playerCardList[id]}。')
        return 0
      if card not in playerCardList[id]:
        self.sendMsg('你没有那张牌！')
        return 0
      if card == '+4':
        for i in playerCardList[id]:
          if i[0] == firstCard[0]:
            self.sendMsg('不符合规则！')
            return 0
        if len(msgList) < 3:
          self.sendMsg('缺少参数！')
          return 0
        if msgList[2] not in '红黄蓝绿':
          self.sendMsg('参数错误！')
          return 0
        firstCard = msgList[2] + '?'
        firstMan = playerList[next2Id]
        for i in range(4):
          addCard = random.choice(cardList)
          playerCardList[nextId].append(addCard)
          cardList.remove(addCard)
        self.sendMsg(f'`{sender}`出了+4（王牌），`{playerList[nextId]}`加四张，颜色变为=={msgList[2]}==，轮到`{firstMan}`！')
        self.sendTo(playerList[nextId], f'你新增了4张牌，这是你现在的牌：{ playerCardList[nextId]}。')
      if card == '变色':
        if len(msgList) < 3:
          self.sendMsg('缺少参数！')
          return 0
        if msgList[2] not in '红黄蓝绿':
          self.sendMsg('参数错误！')
          return 0
        firstMan = playerList[nextId]
        firstCard = msgList[2] + '?'
        self.sendMsg(f'`{sender}`出了变色牌，颜色变为=={msgList[2]}==，轮到`{firstMan}`！')
      if card[0] == firstCard[0] or card[1:] == firstCard[1:] or firstCard == '变色':
        firstCard = card
        if card[1:] == '禁':
          firstMan = playerList[next2Id]
          self.sendMsg(f'`{sender}`出了{card}，`{playerList[nextId]}`跳过1轮，轮到`{firstMan}`！')
        elif card[1:] == '+2':
          firstMan = playerList[next2Id]
          for i in range(2):
            addCard = random.choice(cardList)
            playerCardList[nextId].append(addCard)
            cardList.remove(addCard)
          self.sendMsg(f'`{sender}`出了=={card}==，`{playerList[nextId]}`加2张，轮到`{firstMan}`！')
          self.sendTo(playerList[nextId], f'你新增了2张牌，这是你现在的牌：{playerCardList[nextId]}。')
        elif card[1:] == '转向':
          newPlayerList = []
          newPlayerCardList = []
          for i in range(len(playerList)):
            newPlayerList.insert(0, playerList[i])
            newPlayerCardList.insert(0, playerCardList[i])
          playerList = newPlayerList
          playerCardList = newPlayerCardList
          firstMan = playerList[(-id)%len(playerList)]
          self.sendMsg(f'`{sender}`出了{card}，==顺序转换==，轮到`{firstMan}`！')
        else:
          firstMan = playerList[nextId]
          self.sendMsg(f'`{sender}`出了=={card}==，轮到`{firstMan}`！')
      elif card not in ['+4', '变色']:
        self.sendMsg('不符合规则！')
        return 0
      playerCardList[id].remove(card)
      if len(playerCardList[id]) == 1:
        self.sendMsg(f'`{sender}`==UNO==了！！！')
      if len(playerCardList[id]) == 0:
        self.sendMsg(f'`{sender}`获胜，游戏结束。')
        gameStatus = False
        playerList = []
        playerCardList = [] 
      
      
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
        self.onWhisper(result["from"], "".join(result["text"].split(": ")[1:]))
      elif cmd == "onlineSet":
        self.onSet(result["nicks"], result)
      elif cmd == "warn":
        print(result["text"])


if __name__ == '__main__':
  chat = HackChat("lounge", "UNO", os.getenv("pswd"))
  chat.run()
