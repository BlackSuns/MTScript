import os

from .base import BaseExchange


class CobinhoodExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'cobinhood'
        self.exchange_id = 1395
        self.base_url = 'https://api.cobinhood.com/v1'

        self.ticker_url = '/market/stats'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        print(url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        # print(result)
        return_data = []

        for k in result['result'].keys():
            (symbol, anchor) = str(k).split('-')
            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': result['result'][k]['last_price'],
                    'volume_anchor': float(result['result'][k]['quote_volume']),
                    'volume': float(result['result'][k]['base_volume']),
                })

        # print(return_data)
        return return_data
