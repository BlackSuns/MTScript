import json
import os

from .base import BaseExchange


class ZaifExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'zaif'
        self.exchange_id = 103
        self.base_url = 'https://api.zaif.jp/api/1'

        self.ticker_url = '/ticker'
        self.pair_url = '/currency_pairs/all'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pairs(self):
        url = '{}{}'.format(self.base_url, self.pair_url)
        return self.pair_callback(self.get_json_request(url))

    def pair_callback(self, result):
        support_pairs = {}
        for r in result:
            (symbol, anchor) = r['name'].split('/')
            if symbol == 'BITCRYSTALS':
                symbol = 'BCY'
            if symbol == 'ERC20.CMS':
                symbol = 'CMS.ETH'
            if symbol == 'MOSAIC.CMS':
                symbol = 'CMS.XEM'

            pair = '{}/{}'.format(symbol.upper(), anchor.upper())
            support_pairs[pair] = r['currency_pair']

        return support_pairs

    def get_remote_data(self):
        return_data = []
        pairs = self.get_available_pairs()

        for i, p in enumerate(pairs.keys(), 1):
            # print('dealing {}/{} pair: {}'.format(i, len(pairs), p))
            try:
                url = '{}{}/{}'.format(self.base_url,
                                       self.ticker_url,
                                       pairs[p])
                # print(url)
                r = self.get_json_request(url)
                # print(r)

                data = {
                    'pair': p,
                    'price': r['last'],
                    'volume': r['volume'],
                    'volume_anchor': r['volume'] * r['vwap']
                }

                return_data.append(data)
            except Exception as e:
                print('error happened on {}: {}'.format(p, e))
        return return_data
