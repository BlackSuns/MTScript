import os

from .base import BaseExchange


class CeoExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'ceo'
        self.exchange_id = 1355
        self.base_url = 'https://www.bite.ceo'

        self.ticker_url = '/market/ticker'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for k in result.keys():
            (symbol, anchor) = str(k).split('_')
            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': result[k]['last'],
                    'volume_anchor': float(result[k]['volume_quote']),
                    'volume': float(result[k]['volume']),
                })

        # print(return_data)
        return return_data
