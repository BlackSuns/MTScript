import json
import os
from .base import BaseExchange


class QbtcExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'qbtc'
        self.exchange_id = 1392
        self.base_url = 'http://www.qbtc.com/json'

        self.ticker_url = '/topQuotations.do'

        self.alias = 'qbtc'
        self.with_name = True
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_symbols(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data

    def get_remote_data(self):
        return_data = []
        anchor = 'CNYT'

        symbols = self.get_available_symbols()['name_symbol']
        for symbol in symbols.keys():
            print('dealing {}'.format(symbol))
            try:
                url = '{}{}?tradeMarket={}&symbol={}'.format(self.base_url,
                                                             self.ticker_url,
                                                             anchor,
                                                             symbol)
                # print(url)
                r = self.get_json_request(url)
                price = float(r['result']['last'])
                volume = float(r['result']['volume'])

                data = {
                    'name': symbols[symbol],
                    'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                    'price': price,
                    'volume': volume,
                    'volume_anchor': price * volume
                }

                return_data.append(data)
            except Exception as e:
                print('error happened: {}'.format(e))
        return return_data
