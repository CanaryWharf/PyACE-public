from Agents import BaseAgent
#from Assets import Asset
from pprint import pprint  # NOQA
from Tools import Order

class BaseMarket(BaseAgent):

    def __init__(self, tag=None, debug=False):
        super().__init__()
        self.debug = debug
        self.tag = tag
        self.stock = {}
        self.pricedata = {}

    def get_pricedata(self):
        return dict(self.pricedata)

    def add_supply(self, newitem):
        #print(newitem.agent)
        if not isinstance(newitem, Order):
            raise TypeError("Market only accepts Order objects")
        if newitem.product not in self.stock.keys():
            self.stock[newitem.product] = []
            self.stock[newitem.product].append(newitem)
        else:
            for i, order in enumerate(self.stock[newitem.product]):
                if order.price > newitem.price:
                    self.stock[newitem.product].insert(i, newitem)
                    return
            self.stock[newitem.product].append(newitem)

    def check_stock(self, item=None):
        if item:
            if item in self.stock.keys():
                return list(self.stock[item])
            else:
                return []
        else:
            return dict(self.stock)

    def commit_transaction(self, buyer, seller, product, price, quantity):
        if product not in self.pricedata.keys():
            self.pricedata[product] = []
        self.pricedata[product].append((price, quantity))
        if self.debug:
            print("%s bought %d x %s from %s at $%d a piece" % (buyer.name,
                                                                quantity,
                                                                product,
                                                                seller.name,
                                                                price))
        buyer.withdraw(price * quantity)
        buyer.store(product, quantity)
        seller.deposit(price * quantity)
        seller.remove(product, quantity)

    def balance(self):
        for key, data in self.pricedata.items():
            totalsold = sum([x for y, x in data])
            mini = None
            maxi = None
            totalprice = 0
            for item in data:
                if not mini:
                    mini = item[0]
                    maxi = item[0]
                if item[0] > maxi:
                    maxi = item[0]
                if item[0] < mini:
                    mini = item[0]
                totalprice += item[0]
            print("Product: %s, Average Price: %d, Min Price: %d, Max Price: %d, Sold: %d" % (
                key, totalprice/totalsold, mini, maxi, totalsold))
        self.stock = {}
        self.pricedata = {}
        return True



class RetailStore(BaseMarket):

    def __init__(self, tag=None, debug=False):
        super().__init__(tag, debug)

    def buy_item(self, buyer, item, quantity):
        order = self.stock[item][0]
        if quantity > order.quantity:
            raise ValueError("Agent attempted to buy more than available stock")
        self.commit_transaction(buyer, order.agent, item, order.price, quantity)
        order.quantity -= quantity
        if order.quantity == 0:
            self.stock[item].pop(0)


class BaseAuction(BaseMarket):
    pass

class DoubleAuction(BaseAuction):

    def __init__(self, tag=None, debug=False):
        super().__init__(tag, debug)
        self.bids = {}

    def add_bid(self, bid):
        if not isinstance(bid, Order):
            raise TypeError("Market only accepts Order objects")
        if bid.product not in self.bids.keys():
            self.bids[bid.product] = []
        self.bids[bid.product].append(bid)

    def balance(self):
        self.stock = {}
        self.bids = {}
        return True

    def start_auction(self):
        for key, buyorder in self.bids.items():
            if key not in self.stock.keys():
                continue
            sellorder = self.stock[key]
            #buyorder.sort(reverse=True)
            #sellorder.sort()
            kingq = -1
            kingp = -1
            for item in buyorder:
                cand = self.check_clear(item.price, buyorder, sellorder)
                if cand > kingq:
                    kingq = cand
                    kingp = item.price
            print("Clearing %s at $%s per piece. Estimated sold: %s" % (key, kingp, kingq))
            self.clear(kingp, buyorder, sellorder)
        self.balance()


    def clear(self, price, buyorders, sellorders):
        nubuys = []
        nusells = []
        for item in buyorders:
            if item.price >= price:
                nubuys.append(item)
        for item in sellorders:
            if item.price <= price:
                nusells.append(item)

        for buy in nubuys:
            while buy.quantity > 0 and len(nusells) > 0:
                quantity = min(nusells[0].quantity, buy.quantity)
                buy.quantity -= quantity
                nusells[0].quantity -= quantity
                self.commit_transaction(buy.agent,
                                        nusells[0].agent,
                                        buy.product,
                                        price,
                                        quantity)
                if nusells[0].quantity == 0:
                    nusells.pop(0)




    def check_clear(self, price, buyorder, sellorder):
        buyclears = 0
        sellclears = 0
        for item in buyorder:
            if item.price >= price:
                buyclears += item.quantity
        for item in sellorder:
            if item.price <= price:
                sellclears += item.quantity
        return min(buyclears, sellclears)


class BlindAuction(BaseAuction):
    pass

class EnglishAuction(BaseAuction):
    pass

class DutchAuction(BaseAuction):
    pass

class VickreyAuction(BaseAuction):
    pass




