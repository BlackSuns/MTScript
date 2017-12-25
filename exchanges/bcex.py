import os

from .base import BaseExchange


class BcexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bcex'
        self.exchange_id = 1339
        self.base_url = 'http://www.bcex.ca'

        self.ticker_url = '/coins/markets'

        self.alias = 'BCEX'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        # print(result)
        return_data = []

        for anchor in result['data'].keys():
            for p in result['data'][anchor]:
                symbol = p['coin_from']
                if anchor == 'ckusd':
                    anchor = 'CK.USD'
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': p['current'],
                    'volume_anchor': p['sum'],
                    'volume': p['count'],
                })

        # print(return_data)
        return return_data
