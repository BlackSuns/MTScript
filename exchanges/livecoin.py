import os

from .base import BaseExchange


class LivecoinExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'livecoin'
        self.exchange_id = 145
        self.base_url = 'https://api.livecoin.net'

        self.ticker_url = '/exchange/ticker'

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

        for p in result:
            return_data.append({
                'pair': p['symbol'],
                'price': p['last'],
                'volume_anchor': p['last'] * p['volume'],
                'volume': p['volume'],
            })

        # print(return_data)
        return return_data
