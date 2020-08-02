from flask_table import Table, Col


"""Lets suppose that we have a class that we get an iterable of from
somewhere, such as a database. We can declare a table that pulls out
the relevant entries, escapes them and displays them.
"""


class Item(object):
    def __init__(self, id, symbol, symbolid,size,side,price,usdvalue):
        self.id = id
        self.symbol = symbol
        self.symbolid = symbolid
        self.size = size
        self.side = side
        self.price = price
        self.usdvalue = usdvalue


class ItemTable(Table):
    id = Col('id')
    symbol = Col('symbol')
    symbolid = Col('symbolid')
    size = Col('size')
    side = Col('side')
    price = Col('price')
    usdvalue = Col('usdvalue')
