def intreverse(n):
    rev = 0
    while(n > 0):
        rev = (rev * 10) + (n % 10)
        n = int(n / 10)
    return rev

def isPrime(n):
    if (n <= 1) :
        return False
    if (n <= 3) :
        return True
    if (n % 2 == 0 or n % 3 == 0) :
        return False

    i = 5
    while(i * i <= n) :
        if (n % i == 0 or n % (i + 2) == 0) :
            return False
        i = i + 6

    return True

def sumprimes(l):
    sum = 0;
    for i in range(len(l)):
        if isPrime(l[i]):
            sum = sum + l[i]
    return sum

def matched(s):
    sum = 0
    for i in range(len(s)):
        if s[i] == '(':
            sum = sum + 1
        if (s[i] == ')') and (sum > 0):
            sum = sum - 1
        if (s[i] == ')') and (sum < 0):
            return False
    if sum == 0:
        return True
    else:
        return False

def expanding(l):
    l1 = []
    for i in range(len(l) - 1):
        l1.append(abs(l[i] - l[i+1]))
    for i in range(len(l1) - 1):
        if l1[i] >= l1[i + 1]:
            return False
    return True

def accordian(l):
    l1 = []
    l2 = []
    for i in range(len(l) - 1):
        l1.append(abs(l[i] - l[i+1]))
    for i in range(len(l1) - 1):
        l2.append((l1[i] - l1[i+1]))
    if(len(l2) > 1):
        for i in range(len(l2) - 1):
            if (l2[i] * l2[i+1] >= 0):
                return False
    else:
    	if(l2[0] == 0):
    		return False
    return True

def rotate(m):
    size = len(m)
    m2 = []
    for i in range(size):
        l = []
        j = size - 1
        while(j >= 0):
            l.append(m[j][i])
            j = j - 1
        m2.append(l)
    return m2

def frequency(l):
    l1 = []
    l2 = []
    sortL = l.sort()
    countMax = 0
    countMin = 0
    count = 0
    for i in range(1,len(l)):
        if



class Player:
    def __init__(self, name):
        self.name = name
        self.best5Won = 0
        self.best3Won = 0
        self.setsWon = 0
        self.gamesWon = 0
        self.setsLost = 0
        self.gamesLost = 0

    def __eq__(self, other):
        return self.best5Won == other.best5Won and \
            self.best3Won == other.best3Won and \
            self.setsWon == other.setsWon and \
            self.gamesWon == other.gamesWon and \
            self.setsLost == other.setsLost and \
            self.gamesLost == other.gamesLost

    def __lt__(self, other):
        if self.best5Won < other.best5Won:
            return True
        elif self.best3Won < other.best3Won:
            return True
        elif self.setsWon < other.setsWon:
            return True
        elif self.gamesWon < other.gamesWon:
            return True
        elif self.setsLost > other.setsLost:
            return True
        elif self.gamesLost > other.gamesLost:
            return True
        else:
            return False






# player name vs Player object
players = dict()

while True:
    value = input()
    if value == "":
        break

    [winner, loser, sets] = value.split(":")
    sets = sets.split(",")
    sets = [list(map(int, s.split("-"))) for s in sets ]

    if winner not in players:
        # player does not exist create first time!
        players[winner] = Player(winner)
    winningPlayer = players[winner]

    if loser not in players:
        # player does not exist create first time!
        players[loser] = Player(loser)

    losingPlayer = players[loser]

    winningPlayer.gamesWon = winningPlayer.gamesWon + 1
    losingPlayer.gamesLost = losingPlayer.gamesLost + 1

    if len(sets) == 3:
        winningPlayer.best3Won = winningPlayer.best3Won + 1
    elif len(sets) == 5:
        winningPlayer.best5Won = winningPlayer.best5Won + 1

    for s in sets:
        if (s[1] < s[0]):
            winningPlayer.setsWons = winningPlayer.setsWon + s[0]
            losingPlayer.setsLost = losingPlayer.setsLost + s[1]
        else:
            winningPlayer.setsLost = winningPlayer.setsLost + s[0]
            losingPlayer.setsWon = losingPlayer.setsWon + s[1]


# print stat for each player
#for p in list(players.values()).sort():

for k in players.keys():
    p = players[k]
    print(p.name, p.best5Won, p.best3Won, p.setsWon, p.gamesWon, p.setsLost, p.gamesLost)
