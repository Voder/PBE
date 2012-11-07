#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from time import sleep

from utils import enumerate1, range1, to_pyreadable, ujoin
from board import Board, Loc

size          = 15, 8
num_ships     = 5
pause_time    = 0.3

nl            = '\n'
prompt        = '> '
space         = ' '
tiletpl       = '%3s'
shipchar      = '#'
sunkship      = '%'
blank         = '.'
hitchar       = '*'
quit_key      = 'q'

players       = '1', '2'
manual_player = '2'
divider       = '-' * (size[1]*4 + 20)


class Tile(object):
    """Tile that may be a ship or blank space (water)."""
    ship   = False
    is_hit = False
    hidden = True

    def __init__(self, x, y):
        self.loc = Loc(x, y)

    def __repr__(self):
        return blank if self.hidden else self.char

class Blank(Tile):
    char = blank

    def hit(self):
        self.is_hit = True
        self.char   = hitchar

class Ship(Tile):
    char = shipchar
    ship = True

    def hit(self):
        self.is_hit = True
        self.char   = sunkship


class BattleshipBoard(Board):
    def __init__(self, size):
        super(BattleshipBoard, self).__init__(size, Blank, tiletpl=tiletpl)

    def draw(self):
        print(space*3, ujoin(range1(self.width), tpl=tiletpl), nl )
        for n, row in enumerate1(self.board):
            print(tiletpl % n, ujoin(row, tpl=tiletpl), nl)

    def all_unhit(self):
        return [tile for tile in self if not tile.is_hit]

    def random_unhit(self):
        return rndchoice(self.all_unhit()).loc

    def reveal(self, loc):
        """UNUSED"""
        self[loc].hidden = False
        return self[loc]

    def valid_hidden(self, loc):
        return bool(self.valid(loc) and self[loc].hidden)

    def getloc(self, start, dir, n):
        """Return location offset from `start` point by `n` tiles in direction `dir`."""
        return Loc(start.x + dir.x*n, start.y + dir.y*n)

    def random_blank(self):
        return rndchoice( [tile for tile in self if not tile.ship] )

    def valid_blank(self, loc):
        return bool( self.valid(loc) and not self[loc].ship )

    def random_placement(self, ship):
        """Return list of random locations for `ship` length."""
        dirs  = [Loc(*d) for d in ((1,0), (0,1), (-1,0), (0,-1))]
        print("ship", ship)

        while True:
            start = self.random_blank().loc
            dir   = rndchoice(dirs)
            print ("start", start)
            print ("dir", dir)
            print ( self.getloc(start, dir, 1) )
            locs  = [ self.getloc(start, dir, n) for n in range(ship) ]

            print ("locs", locs)
            if all(self.valid_blank(loc) for loc in locs):
                break
        print ("locs", locs)
        return locs


class Player(object):
    def __init__(self, num):
        """Create player's board and randomly place `num_ships` ships on it."""
        self.num = num
        B = self.board = BattleshipBoard(size)

        for ship in range1(num_ships):
            for loc in B.random_placement(ship):
                B[loc] = Ship(*loc)

        self.is_manual = bool(self.num == manual_player)

        if self.is_manual:
            print("is_manual, revealing all my tiles")
            for tile in B:
                tile.hidden = False

    def enemy(self):
        return players[0] if players[1] is self else players[1]


class Battleship(object):
    losemsg = "All ships are sunk! Player %s loses the game!"

    def draw(self):
        p1, p2 = players

        print(nl*5)
        p1.board.draw()
        print(divider)
        p2.board.draw()

    def check_end(self, player):
        if not any( tile.ship and tile.hidden for tile in player.board ):
            self.game_lost(player)

    def game_lost(self, player):
        print(losemsg % player.num)
        sys.exit()


class Test(object):
    def run(self):
        while True:
            for player in players:
                bship.draw()
                self.manual_move(player) if player.is_manual else self.ai_move(player)
            print(divider)

    def manual_move(self, player):
        while 1:
            try:
                self._manual_move(player)
                return
            except (IndexError, ValueError, TypeError):
                continue

    def _manual_move(self, player):
        """Get user command and reveal the tile; check if game is won/lost."""
        inp = raw_input(prompt)
        if inp == quit_key: sys.exit()

        x, y = to_pyreadable(inp.split())
        tile = board[ Loc(x, y) ]
        tile.hidden = False
        bship.check_end(player.enemy())

    def ai_move(self, player):
        """Very primitive `AI', always hits a random location."""
        B = player.enemy().board
        B[ B.random_unhit() ].hidden = False
        sleep(pause_time)


if __name__ == "__main__":
    players = [Player(p) for p in players]
    bship   = Battleship()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
