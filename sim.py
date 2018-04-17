import Agents
from World import World
from Tools import Utility
from pprint import pprint  # NOQA
import Market
import random


# Variables to change
UTILITY_FUNCTION = "fish^0.5 + chips^0.5"
NUMBER_OF_FISH = 100
NUMBER_OF_CHIPS = 100


class Shop(Agents.SmartProducer):
    forget_rate = 0.1

    def __init__(self, product):
        super().__init__(product)
        self.round_score = 0
        self.starting_cash = 0
        self.strategies = [
            self.raise_price,
            self.lower_price,
            self.expand,
            self.downsize,
            self.do_nada
        ]
        self.rate = random.randint(1, 3)
        self.turns = {
            0: self.choose,
            1: self.produce,
            2: self.put_on_market,
            4: self.calculate_score

        }

    def calculate_score(self):
        change = self.cash - self.starting_cash
        self.starting_cash = self.cash
        self.round_score = change


    def produce(self):
        self.store(self.product, self.rate)
        self.cash -= self.cost * self.rate

    def raise_price(self):
        self.price += 2

    def lower_price(self):
        self.price = max(self.price - 2, self.cost)

    def do_nada(self):
        pass

    def expand(self):
        self.rate += 1

    def downsize(self):
        self.rate = max(1, self.rate - 1)

class Shopper(Agents.Consumer):

    def __init__(self, utility, mps=0.1):
        super().__init__(utility, mps)
        self.income = random.randint(50, 200)
        self.turns = {
            0: self.work,
            3: self.shop,
            4: self.consume

        }

    def work(self):
        self.cash += self.income

    def consume(self):
        for item in self.inventory.keys():
            self.inventory[item] = 0


market = Market.RetailStore()
world = World(5)
world.add_market(market)
world.make_agents(Shopper, 1000, Utility(UTILITY_FUNCTION))
world.make_agents(Shop, NUMBER_OF_FISH, "fish")
world.make_agents(Shop, NUMBER_OF_CHIPS, "chips")
world.run_sim(100)
world.show_data()
