import os

from .base import BaseExchange


class CoinexchangeExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'coinexchange'
        self.exchange_id = 97
        self.base_url = 'https://www.coinexchange.io/api/v1'

        self.pair_url = '/getmarkets'
        self.ticker_url = '/getmarketsummaries'

        self.alias = ''
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
        self.support_pairs = {}
        for r in result['result']:
            if r['Active']:
                self.support_pairs[r['MarketID']] = '{}/{}'.format(
                        r['MarketAssetCode'].upper(),
                        r['BaseCurrencyCode'].upper()
                    )

    def get_remote_data(self):
        url = '{}{}'.format(self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []
        self.get_available_pair()

        for r in result['result']:
            if r['MarketID'] in self.support_pairs.keys():
                price = float(r['LastPrice'])
                volume = float(r['Volume'])
                return_data.append({
                    'pair': self.support_pairs[r['MarketID']],
                    'price': price,
                    'volume': volume,
                    'volume_anchor': volume * price
                })

        return return_data
