import os

from .base import BaseExchange


class BiboxExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'Bibox'
        self.exchange_id = 1370
        self.base_url = 'https://api.bibox.com/v1'

        self.ticker_url = '/mdata?cmd=marketAll'

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

        for t in result['result']:
            symbol = t['coin_symbol']
            anchor = t['currency_symbol']

            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': float(t['last']),
                    'volume_anchor': float(t['amount']),
                    'volume': float(t['vol24H']),
                })

        # print(return_data)
        return return_data
