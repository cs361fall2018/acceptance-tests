import requests as req
import json

lastCheck = False

class Game:
    URL = "http://localhost:8080/"
    PLACE = URL + "place"
    ATTACK = URL + "attack"
    GAME = URL + "game"

    game = {}
    lastStatus = 0

    def __init__(self):
        self.game = self.__getGame()

    def __getGame(self):
        resp = req.get(self.GAME)
        return json.loads(resp.text)

    def placeShip(self, shipType, x, y, isVertical):
        resp = req.post(self.PLACE, json={'game': self.game, 'shipType': shipType, 'x': x, 'y': y, 'isVertical': False})
        self.lastStatus = resp.status_code
        if (self.lastStatus == 200):
            self.game = json.loads(resp.text)

    def attack(self, x, y):
        resp = req.post(self.ATTACK, json={'game': self.game, 'x': x, 'y': y})
        self.lastStatus = resp.status_code
        if (self.lastStatus == 200):
            self.game = json.loads(resp.text)

    def getPlayersShips(self):
        return self.game['playersBoard']['ships']

    def getOpponentsShips(self):
        return self.game['opponentsBoard']['ships']

def check(expected, actual, message, value=1, assertion=lambda a, b: a == b):
    global lastCheck
    score = 0
    if (assertion(expected, actual)):
        result = "[OK]"
        score = value
        lastCheck = True
    else:
        result = "[FAILED]"
        lastCheck = False
    print('{}{}{}'.format(message, ' '*(80-len(message+result)), result))
    return score

if __name__ == "__main__":
    score = 0;

    game = Game()
    game.placeShip("MINESWEEPER", 1, "A", False)
    score += check(game.lastStatus, 200, "Minesweeper placement succeeded")
    playersShips = game.getPlayersShips()

    score += check(len(playersShips), 1, "Minesweeper was placed")
    if (lastCheck == True):
        squares = playersShips[0]['occupiedSquares']
        score += check(len(squares), 2, "Minesweeper occupies 2 squares")

    game.placeShip("MINESWEEPER", 1, "A", False)
    score += check(game.lastStatus, 200, "Cannot overlap ships", assertion=lambda a, b: a != b)

    game.placeShip("MINESWEEPER", 11, "A", False)
    score += check(game.lastStatus, 200, "Cannot place outside board", assertion=lambda a, b: a != b)

    game.placeShip("DESTROYER", 2, "A", False)
    score += check(game.lastStatus, 200, "Destroyer placement succeeded")
    playersShips = game.getPlayersShips()

    score += check(len(playersShips), 2, "Destroyer was placed")
    if (lastCheck == True):
        squares = playersShips[1]['occupiedSquares']
        score += check(len(squares), 3, "Destroyer occupies 3 squares")

    game.placeShip("BATTLESHIP", 3, "A", True)
    score += check(game.lastStatus, 200, "Battleship placement succeeded")
    playersShips = game.getPlayersShips()

    score += check(len(playersShips), 3, "Battleship was placed")
    if (lastCheck == True):
        squares = playersShips[2]['occupiedSquares']
        score += check(len(squares), 4, "Battleship occupies 3 squares")

    game.placeShip("DESTROYER", 4, "A", False)
    score += check(game.lastStatus, 200, "Cannot place more than 3 ships", assertion=lambda a, b: a != b)

    shipsToSink = game.getOpponentsShips()
    score += check(len(shipsToSink), 3, "Opponent placed 3 ships")

    for ship in shipsToSink:
        squares = ship['occupiedSquares']
        total = len(squares)
        for square in squares:
            game.attack(square['row'], square['column'])

    if (game.game['opponentsBoard']['attacks'] != None):    
        sunks = [x for x in game.game['opponentsBoard']['attacks'] if x['result'] == 'SUNK']
        hits = [x for x in game.game['opponentsBoard']['attacks'] if x['result'] == 'HIT']
        surrenders = [x for x in game.game['opponentsBoard']['attacks'] if x['result'] == 'SURRENDER']

        score += check(len(hits), 6, "We have the correct number of hits")
        score += check(len(sunks), 2, "We have the correct number of sunks")
        score += check(len(surrenders), 1, "We have the correct number of surrenders")

    print('Final Score: ' + str(score))
