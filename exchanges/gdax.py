import os
import time

from .base import BaseExchange


class GdaxExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'gdax'
        self.exchange_id = 7
        self.base_url = 'https://api.gdax.com'

        self.pair_url = '/products'
        self.ticker_url = '/products'

        self.alias = 'gdax'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    # get all available_pairs
    # update result to self.support_pairs
    # self.support_pairs is a list
    def get_available_pair(self):
        url = '{}{}'.format(self.base_url, self.pair_url)
        self.pair_callback(self.get_json_request(url))

    def pair_callback(self, result):
        self.support_pairs = []
        for p in result:
            self.support_pairs.append(p['id'])

    def get_remote_data(self):
        self.get_available_pair()
        return_data = []
        for pair in self.support_pairs:
            try:
                url = '{}{}/{}/ticker'.format(
                    self.base_url, self.ticker_url, pair)
                r = self.ticker_callback(self.get_json_request(url))
                r['pair'] = pair.replace('-', '/')
                return_data.append(r)
                time.sleep(0.2)
            except Exception as e:
                print(e)
        return return_data

    def ticker_callback(self, result):
        price = float(result['price'])
        volumn = float(result['volume'])
        return {
            'price': price,
            'volume': volumn,
            'volume_anchor': price * volumn,
        }
