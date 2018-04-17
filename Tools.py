import re


class Inventory:

    def __init__(self):
        self.storage = {}

    def __setitem__(self, key, value):
        self.storage[key] = value

    def keys(self):
        return self.storage.keys()

    def __getitem__(self, index):
        if index not in self.storage.keys():
            self.storage[index] = 0
        return self.storage[index]


class Utility:
    """The utility function. Accepts utility in the form 'base product^alpha + base product^alpha'"""

    def __init__(self, utility):
        self.prodlist = {}
        self.string_value = utility
        self.set_utility(utility)

    def add_product(self, name, alpha, base=0):
        self.prodlist[name] = [base, alpha]

    def set_utility(self, utility):
        regex = re.compile('(([0-9]*?) ?([a-zA-Z]+)\^([0-9\.]+))')
        mo = regex.findall(utility)
        for entry in mo:
            self.prodlist[entry[2]] = [int(entry[1]) if entry[1] else 0, float(entry[3])]
            if self.prodlist[entry[2]][1] > 1 or self.prodlist[entry[2]][1] < 0:
                raise ValueError("Alpha values must be between 0 and 1")

    def get_alpha(self, name):
        return self.prodlist[name][1]

    def get_base(self, name):
        return self.prodlist[name][0]

    def get_products(self):
        return list(self.prodlist.keys())

    def get_utility(self):
        return dict(self.prodlist)

    def __str__(self):
        return self.string_value

    def __repr__(self):
        return self.__str__()

class Order:

    def __init__(self, agent, product, price, quantity=1):
        self.product = product
        self.price = price
        self.quantity = quantity
        self.agent = agent

    def __str__(self):
        """Returns a summary of the order"""
        return "%s x %d at $%d a piece" % (self.product, self.quantity, self.price)

    def __repr__(self):
        """returns __str___"""
        return self.__str__()

    def __radd__(self, other):
        """Reverse add the quantity of another Order object to this """
        return self.quantity + other

    def __add__(self, other):
        """add the quantity of another Order object to this"""
        return self.quantity + other

    def __lt__(self, other):
        """Check if the price of this Order object is less than the other Order object"""
        return self.price < other.price

    def __gt__(self, other):
        """Check if the price of this Order object is greater than the other Order object"""
        return self.price > other.price
