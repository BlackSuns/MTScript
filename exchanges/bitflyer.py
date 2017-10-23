import os
from .base import BaseExchange


class BitflyerExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bitFlyer'
        self.exchange_id = 17
        self.base_url = 'https://api.bitflyer.jp/v1'

        self.pair_url = '/getmarkets'
        self.ticker_url = '/ticker'

        self.alias = 'bitFlyer'
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
        for r in result:
            if 'product_code' in r.keys():
                if not str(r['product_code']).startswith('FX_') and \
                   '_' in str(r['product_code']):
                    self.support_pairs.append(r['product_code'])

    def get_remote_data(self):
        return_data = []
        self.get_available_pair()

        for p in self.support_pairs:
            url = '{}{}?product_code={}'.format(
                self.base_url, self.ticker_url, p)
            return_data.append(
                self.ticker_callback(self.get_json_request(url)))

        return return_data

    def ticker_callback(self, result):
            pair = result['product_code'].upper().replace('_', '/')

            return {
                    'pair': pair,
                    'price': result['best_bid'],
                    'volume_anchor': result['volume_by_product'] * result['best_bid'],
                    'volume': result['volume_by_product'],
            }
