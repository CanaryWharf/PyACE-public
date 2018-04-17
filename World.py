from Agents import BaseAgent
from Market import BaseMarket
import numpy as np  # NOQA
import matplotlib.pyplot as plt
from pprint import pprint  # NOQA


class World:

    def __init__(self, turns, death=True, db=None, interval=5):
        self.turns = turns
        self.agents = []
        self.agentcount = {}
        self.death = death
        self.markets = []
        self.db = db
        self.interval = interval
        self.ignore = {'strategies', 'turns'}

    def get_count(self, classname):
        return self.agentcount[classname]

    def sanitise_dict(self, d):
        l = {}
        k = [str, dict, list, int, float, complex]
        for key, value in d.items():
           if not key.startswith("_") and key not in self.ignore and type(value) in k:
                l[key] = value
        return l

    def store_data(self, turn):
        data = {
            "Agents": [],
            "Sales": [],
            "turn": turn
                }
        for agent in self.agents:
            data["Agents"].append(self.sanitise_dict(agent.__dict__))
        for product, pricedata in self.data['sales'][turn].items():
            sales = pricedata['full']
            for item in sales:
                p = {
                    "Product": product,
                    "Price": item[0],
                    "Quantity": item[1]
                }
                data["Sales"].append(p)
        self.db.sim.insert_one(data)

    def make_agents(self, agentbase, num, *args):
        if not issubclass(agentbase, BaseAgent):
            raise TypeError("Agent must inherit from BaseAgent")
        self.count(agentbase.__name__, num)
        if args:
            for i in range(num):
                self.agents.append(agentbase(*args))
        else:
            for i in range(num):
                self.agents.append(agentbase())

    def count(self, name, num=1):
        if name not in self.agentcount.keys():
            self.agentcount[name] = 0
        self.agentcount[name] += num


    def add_agent(self, agent):
        if not issubclass(agent.__class__, BaseAgent):
            raise TypeError("Agent must inherit from BaseAgent")
        self.count(agent.__class__.__name__)
        self.agents.append(agent)

    def add_market(self, agent):
        if not issubclass(agent.__class__, BaseMarket):
            raise TypeError("Market must inherit from BaseMarket")
        self.markets.append(agent)

    def get_market(self, tag=None):
        if tag:
            for market in self.markets:
                if market.tag == tag:
                    return market
            raise KeyError("Market not found")
        else:
            return self.markets[0]

    def print_remaining(self):
        print("Agents Remaining")
        for key, value in self.agentcount.items():
            print("%s: %d remaining" % (key, value))

    def show_data(self):
        prices = {}
        for turnno, v in self.data['sales'].items():
            for product, data in v.items():
                if product not in prices.keys():
                    prices[product] = {}
                if turnno not in prices[product].keys():
                    prices[product][turnno] = []
                for item in data['full']:
                    prices[product][turnno].extend([item[0] for i in range(item[1])])

        leg = []
        for key, entry in prices.items():
            data = []
            errs = []
            for turn in entry.values():
                data.append(np.mean(turn))
                errs.append(max(turn) - min(turn))
            #x = plt.errorbar([i for i in range(len(data))], data, yerr=errs, fmt='o')
            x = plt.scatter([i for i in range(len(data))], data, color='steelblue' if key == "fish" else 'darkorange')
            leg.append(x)
        plt.legend(leg, prices.keys())
        plt.show()



    def run_sim(self, iterations):
        self.data = {'sales': {}}
        self.print_remaining()
        for agent in self.agents + self.markets:
            agent.register_world(self)
            agent.initial_turn()
        for x in range(iterations):
            self.data['sales'][x] = {}
            for agent in self.agents + self.markets:
                agent.preround()
            for i in range(self.turns):
                print("Round: %d, Turn: %d" % (x, i))
                self.data['population'] = len(self.agents)
                for agent in self.agents:
                    agent.doturn(i)
            if self.death:
                self.agentcount = {}
                survivors = []
                for agent in self.agents:
                    if agent.balance():
                        if hasattr(agent, 'product'):
                            self.count(agent.product)
                        else:
                            self.count(agent.__class__.__name__)
                        survivors.append(agent)
                if not survivors:
                    print("Everyone has died. round: %d, turn %d" % (x, i))
                    return
                else:
                    change = len(survivors)
                    if change:
                        self.print_remaining()
                        self.agents = survivors
            else:
                for agent in self.agents:
                    agent.balance()
            for market in self.markets:
                pricedata = market.get_pricedata()
                for k, v in pricedata.items():
                    self.data['sales'][x][k] = {
                        "full": v
                    }
                market.balance()
            for agent in self.agents + self.markets:
                agent.postround()
            print("-"*20)
            if self.db:
                if x % self.interval == 0:
                    self.store_data(x)

