import random
import uuid
from pprint import pprint  # NOQA
from Tools import Order, Inventory
from numpy import random as nprand

class BaseAgent:
    """The Agent from which all other agents are made"""

    def __init__(self, cash=0):
        self.name = uuid.uuid4()
        self.cash = cash
        self.inventory = Inventory()
        self.turns = {}

    def initial_turn(self):
        pass

    def register_world(self, world):
        self.world = world

    def doturn(self, turn):
        if turn in self.turns.keys():
            self.turns[turn]()

    def store(self, product, quantity=1):
        if product not in self.inventory.keys():
            self.inventory[product] = 0
        self.inventory[product] += quantity
        assert self.inventory[product] >= 0

    def remove(self, product, quantity=1):
        self.inventory[product] -= quantity
        assert self.inventory[product] >= 0

    def deposit(self, amount):
        self.cash += amount
        #assert self.cash >= 0

    def withdraw(self, amount):
        self.cash -= amount
        #assert self.cash >= 0

    def balance(self):
        return True

    def preround(self):
        pass

    def postround(self):
        pass

class SmartAgent(BaseAgent):

    def choose(self):
        if not hasattr(self, "weights"):
            eq = len(self.strategies)
            self.score = [0 for i in range(eq)]
        # Make scores positive
        mini = abs(min(self.score))
        nuscore = [x + mini + 1 for x in self.score]
        total = sum(nuscore)
        # Caclulate the probabilities for each strategy
        weights = [x/total for x in nuscore]
        # make random choice
        # Uses Numpy's weighted choice
        self.chosen = nprand.choice([i for i in range(len(self.strategies))], p=weights)
        # Call the chosen method
        self.strategies[self.chosen]()

    def balance(self):
        change = self.round_score - self.previous_score
        for item in self.score:
            item *= (1 - self.forget_rate)
        self.score[self.chosen] += change

    def preround(self):
        self.previous_score = self.round_score



class Producer(BaseAgent):

    def __init__(self, product, price=None, cost=None):
        super().__init__()
        self.product = product
        self.cost = cost if cost else random.randint(1, 10)
        self.price = price if price else random.randint(self.cost, self.cost*3)

    def produce(self):
        raise NotImplementedError("Override the produce() mehtod in Producer class")

    def put_on_market(self):
        if self.inventory[self.product] > 0:
            order = Order(self, self.product, self.price, self.inventory[self.product])
            self.world.get_market().add_supply(order)

    def balance(self):
        return self.cash >= -10

class SmartProducer(Producer, SmartAgent):
    def __init__(self, product, price=None, cost=None):
        Producer.__init__(self, product, price, cost)

    def balance(self):
        SmartAgent.balance(self)
        return Producer.balance(self)

class Consumer(BaseAgent):

    def __init__(self, utility, mps=0.2):
        super().__init__()
        self.utility = utility
        self.alive = True
        self.mps=mps


    def work(self):
        raise NotImplementedError("Override the work() method in Consumer class")

    def shop(self):
        m = self.world.get_market()
        shoplist = self.utility.get_products()
        # Meet base consumption
        for product in shoplist:
            base = self.utility.get_base(product)
            if base == 0:
                continue
            stock = m.check_stock(product)
            while stock:
                item = stock[0]
                quant = min(base, item.quantity)
                if quant * item.price > self.cash:
                    self.alive = False
                    return
                m.buy_item(self, product, quant)
                base -= quant
                if base == 0:
                    break
                stock = m.check_stock(product)
            if base > 0:
                self.alive = False
                return

        # Save according to MPS
        disposable_cash = self.cash * (1-self.mps)
        for product in shoplist:
            alpha = self.utility.get_alpha(product)
            spend = alpha * disposable_cash
            stock = m.check_stock(product)
            while stock:
                item = stock[0]
                quant = min(int(spend/item.price), item.quantity)
                if quant == 0:
                    break
                total = quant * item.price
                m.buy_item(self, product, quant)
                spend -= total
                self.cash -= total
                if spend <= item.price:
                    break
                stock = m.check_stock(product)


    def balance(self):
        return self.alive
