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

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pairs(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data['pairs']

    def get_remote_data(self):
        return_data = []
        pairs = self.get_available_pairs()
        for i, p in enumerate(pairs, 1):
            print('dealing {}/{} pair: {}'.format(i, len(pairs), p))
            try:
                (symbol, anchor) = p.split('_')
                url = '{}{}/{}'.format(self.base_url,
                                       self.ticker_url,
                                       str(p).lower())
                # print(url)
                r = self.get_json_request(url)

                price = r['last']
                volume = r['volume']

                data = {
                    'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                    'price': price,
                    'volume': volume,
                    'volume_anchor': price * volume
                }

                return_data.append(data)
            except Exception as e:
                print('error happened on {}: {}'.format(p, e))
        return return_data
