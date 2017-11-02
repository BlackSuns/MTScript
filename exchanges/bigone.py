import os

from .base import BaseExchange


class BigoneExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bigone'
        self.exchange_id = 1352
        self.base_url = 'https://api.big.one'

        self.ticker_url = '/markets'

        self.alias = 'bigone'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        print(url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for c in result['data']:
            symbol = c['quote']
            anchor = c['base']
            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                price = float(c['ticker']['price'])
                vol = float(c['ticker']['volume'])
                return_data.append({
                    'pair': pair,
                    'price': price,
                    'volume_anchor': price * vol,
                    'volume': vol,
                })

        # print(return_data)
        return return_data
