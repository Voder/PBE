from __future__ import print_function, unicode_literals, division
from utils import ujoin


class Loc(object):
    def __init__(self, x, y):
        self.loc = x, y
        self.x, self.y = x, y

    def __repr__(self):
        return str(self.loc)

    def __iter__(self):
        return iter(self.loc)

    def moved(self, x, y):
        """ Return a new Loc moved according to delta modifiers `x` and `y`,
            e.g. 1,0 to move right.
        """
        return Loc(self.x + x, self.y + y)


class CommonBoard(object):
    def __init__(self, size, tiletpl="%s"):
        if isinstance(size, int):
            size = size, size   # square board
        self.width, self.height = size
        self.tiletpl = tiletpl

    def __iter__(self):
        return ( self[Loc(x, y)] for x in range(self.width) for y in range(self.height) )

    def locations(self):
        return (Loc(x, y) for x in range(self.width) for y in range(self.height))

    def valid(self, loc):
        return bool( loc.x >= 0 and loc.y >= 0 and loc.x <= self.width-1 and loc.y <= self.height-1 )

    def neighbour_locs(self, tile):
        """Return the generator of neighbour locations of `tile`."""
        x, y = tile.loc
        coords = (-1,0,1)
        locs = set((x+n, y+m) for n in coords for m in coords) - set( [(x,y)] )
        return ( Loc(*tpl) for tpl in locs if self.valid(Loc(*tpl)) )

    def neighbours(self, tile):
        """Return the generator of neighbours of `tile`."""
        return (self[loc] for loc in self.neighbour_locs(tile))

    def neighbour_cross_locs(self, tile):
        """Return the generator of neighbour 'cross' (i.e. no diagonal) locations of `tile`."""
        x, y = tile.loc
        locs = ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
        return ( Loc(*tpl) for tpl in locs if self.valid(Loc(*tpl)) )

    def cross_neighbours(self, tile):
        """Return the generator of 'cross' (i.e. no diagonal) neighbours of `tile`."""
        return (self[loc] for loc in self.neighbour_cross_locs(tile))

    def make_tile(self, x, y):
        """Make a tile using `self.def_tile`. If def_tile is simply a string, return it, otherwise instantiate with x, y as arguments."""
        return self.def_tile if isinstance(self.def_tile, basestring) else self.def_tile(x, y)


class Board(CommonBoard):
    def __init__(self, size, def_tile, **kwargs):
        super(Board, self).__init__(size, **kwargs)

        self.def_tile = def_tile
        self.board = [ [self.make_tile(x, y) for x in range(self.width)] for y in range(self.height) ]

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x] = item

    def __delitem__(self, loc):
        self.board[loc.y][loc.x] = self.make_tile(loc.x, loc.y)

    def draw(self):
        for row in self.board:
            print(ujoin(row, '', tpl=self.tiletpl))


class StackableBoard(CommonBoard):
    def __init__(self, size, def_tile, **kwargs):
        super(StackableBoard, self).__init__(size, **kwargs)

        self.def_tile = def_tile
        self.board = [ [[self.make_tile(x, y)] for x in range(self.width)] for y in range(self.height) ]

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x][-1]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x].append(item)

    def __delitem__(self, loc):
        del self.board[loc.y][loc.x][-1]

    def draw(self):
        for row in self.board:
            print(ujoin( (i[-1] for i in row), tpl=self.tiletpl))