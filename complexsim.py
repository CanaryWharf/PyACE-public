import Agents
from World import World
from Tools import Utility, Order
from pprint import pprint  # NOQA
import Market
import random


#client = MongoClient('localhost', 27017)
#db = client.pyace


class Firm(Agents.SmartProducer):

    def __init__(self, product, **kwargs):
        super().__init__(product, **kwargs)
        self.rate = 10
        self.deposit(3000)
        self.forget_rate = 0.2
        self.hours = 10
        self.round_score = 0
        self.price = random.randint(self.minprice, 100)
        self.wage = 21
        self.strategies = [
            self.expand,
            self.downsize,
            self.raise_prices,
            self.lower_prices,
            self.raise_wages,
            self.lower_wages,
            self.do_nothing
        ]


    def preround(self):
        self.withdraw(100)
        self.previous_score = self.round_score

    def hire_workers(self):
        hours_remaining = self.hours
        m = self.world.get_market()
        while hours_remaining > 0:
            stock = m.check_stock("hours")
            if stock:
                q = min(stock[0].quantity, hours_remaining)
                if stock[0].price > self.cash:
                    break
                hours_remaining -= q
                #print(q)
                m.buy_item(self, "hours", q)
            else:
                break



    def expand(self):
        self.hours += 1

    def downsize(self):
        self.hours -= 1

    def raise_prices(self):
        self.price *= 1.1

    def lower_prices(self):
        self.price = max(self.minprice, self.price * 0.9)

    def raise_wages(self):
        self.wage += 1

    def lower_wages(self):
        self.wage = max(self.wage - 1, 1)

    def do_nothing(self):
        pass


class Factory(Firm):


    def __init__(self, product, **kwargs):
        self.minprice = 60
        super().__init__(product, **kwargs)
        self.turns = {
            4: self.shop_for_ingredients,
            5: self.hire_workers,
            6: self.make_product,
            7: self.put_on_market,
            9: self.choose
        }

    def shop_for_ingredients(self):
        forecasted_production = self.rate * self.hours
        m = self.world.get_market()
        for item in ['flour', 'milk', 'eggs']:
            amount_needed = forecasted_production - self.inventory[item]
            while amount_needed > 0:
                stock = m.check_stock(item)
                if stock:
                    if stock[0].price > self.cash:
                        break
                    m.buy_item(self, item, min(stock[0].quantity, amount_needed))
                else:
                    break

    def make_product(self):
        labor_capacity = self.rate * self.inventory["hours"]
        ingredient_capacity = min(self.inventory['flour'],
                                  self.inventory['milk'],
                                  self.inventory['eggs'])
        amount_made = min(labor_capacity, ingredient_capacity)
        for item in ['flour', 'eggs', 'milk']:
            self.inventory[item] -= amount_made
        self.inventory["hours"] = 0
        self.store(self.product, amount_made)

class Farm(Firm):

    def __init__(self, product, **kwargs):
        self.minprice = 22
        super().__init__(product, **kwargs)
        self.turns = {
                1: self.hire_workers,
                2: self.make_product,
                3: self.put_on_market,
                9: self.choose
            }
    def make_product(self):
        amount_made = self.rate * self.inventory['hours']
        self.store(self.product, amount_made)
        self.inventory['hours'] = 0



class Plebian(Agents.Consumer, Agents.SmartAgent):

    def __init__(self):
        Agents.Consumer.__init__(self, Utility("1 cakes^0.5 + 1 brownies^0.5"), mps=0.2)
        self.deposit(300)
        self.forget_rate = 0.2
        self.expected_salary = 20
        self.strategies = [
            self.raise_salary,
            self.lower_salary,
            #self.save_more,
            #self.spend_more,
            self.do_nothing
        ]

        self.turns = {
            0: self.work,
            8: self.shop,
            9: self.choose
        }

    def preround(self):
        self.previous_score = self.round_score
        self.inventory['hours'] = 16

    def initial_turn(self):
        self.round_score = 0

    def work(self):
        m = self.world.get_market()
        order = Order(self, "hours", self.expected_salary, self.inventory['hours'])
        m.add_supply(order)

    def save_more(self):
        self.mps = min(1, self.mps + 0.01)

    def spend_more(self):
        self.mps = max(0.0, self.mps - 0.01)

    def raise_salary(self):
        self.expected_salary += 1

    def lower_salary(self):
        self.expected_salary = max(1, self.expected_salary - 1)

    def do_nothing(self):
        pass

    def balance(self):
        self.round_score = self.inventory['cakes'] + self.inventory['brownies'] + (self.cash * 0.2)
        self.inventory['cakes'] = 0
        self.inventory['brownies'] = 0
        Agents.SmartAgent.balance(self)
        return Agents.Consumer.balance(self)



terra = World(10)
market = Market.RetailStore(debug=False)
terra.make_agents(Plebian, 1000)
for item in ["flour", "milk", "eggs"]:
    for i in range(20):
        agent = Farm(item)
        terra.add_agent(agent)
for item in ["cakes", "brownies"]:
    for i in range(20):
        agent = Factory(item)
        terra.add_agent(agent)
terra.add_market(market)
terra.run_sim(10)
