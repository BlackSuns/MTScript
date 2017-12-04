import json
import os

from bitshares.market import Market

from .base import BaseExchange


class BtsExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bts'
        self.exchange_id = 1371
        self.base_url = 'https://www.bite.ceo'

        self.ticker_url = '/market/ticker'

        self.alias = ''
        self.with_name = True
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pair(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data

    def get_float(self, string):
        try:
            num = string.split(' ')[0]
            num.replace(',', '')
            num = float(num)
        except:
            num = 0

        return num

    def get_remote_data(self):
        return_data = []
        data = self.get_available_pair()

        for symbol in data['symbols'].keys():
            for anchor in data['anchors'].keys():
                try:
                    if symbol != anchor:
                        print('dealing {} : {}'.format(symbol, anchor))
                        market = Market('{}:{}'.format(symbol, anchor))
                        ticker = market.ticker()

                        symbol_ticker = {
                            'name': data['symbols'][symbol]['name'],
                            'pair': '{}/{}'.format(symbol, anchor),
                            'price': self.get_float(ticker['latest']),
                            'volume': self.get_float(ticker['quoteVolume']),
                            'volume_anchor': self.get_float(ticker['baseVolume'])
                        }

                        print(symbol_ticker)

                        if symbol_ticker['price'] > 0 and symbol_ticker['volume'] > 0:
                            return_data.append(symbol_ticker)
                except Exception as e:
                    print(e)

        print(return_data)
        # return return_data
