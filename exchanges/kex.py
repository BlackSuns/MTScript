import os

from .base import BaseExchange


class KexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'kex'
        self.exchange_id = 1374
        self.base_url = 'https://www.kex.com/real'

        self.ticker_url = '/indexmarket.html'

        self.alias = ''
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

        for i in result['data']:
            pair = '{}/{}'.format(i['sellname'].upper(), i['buyname'].upper())
            return_data.append({
                'pair': pair,
                'price': i['price'],
                'volume_anchor': i['total'] * i['price'],
                'volume': i['total'],
            })

        # print(return_data)
        return return_data
