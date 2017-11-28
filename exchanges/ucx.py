import os

from .base import BaseExchange


class UcxExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'ucx'
        self.exchange_id = 1368
        self.base_url = 'http://u.cx/api'

        self.ticker_url = '/trade/all/'

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
                price = float(result[k]['new_price'])
                amount = float(result[k]['amount'])
                volume = amount / price if price > 0 else 0
                return_data.append({
                    'pair': pair,
                    'price': price,
                    'volume_anchor': amount,
                    'volume': volume,
                })

        # print(return_data)
        return return_data
