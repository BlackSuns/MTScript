import json
import os

from .base import BaseExchange


class KorbitExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'korbit'
        self.exchange_id = 111
        self.base_url = 'https://api.korbit.co.kr/v1'

        self.ticker_url = '/ticker/detailed'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_pairs(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data['name_symbol'].keys()

    def get_remote_data(self):
        anchor = 'KRW'
        pairs = self.get_pairs()
        return_data = []
        for p in pairs:
            try:
                pair = '{}/{}'.format(p.upper(), anchor)
                param = '{}_{}'.format(p.lower(), anchor.lower())
                url = '{}{}?currency_pair={}'.format(
                    self.base_url, self.ticker_url, param)
                r = self.ticker_callback(self.get_json_request(url))
                r['pair'] = pair
                return_data.append(r)
            except Exception as e:
                print(e)

        return return_data

    def ticker_callback(self, result):
        price = float(result['last'])
        volume = float(result['volume'])

        return {
            'price': price,
            'volume': volume,
            'volume_anchor': price * volume,
        }
