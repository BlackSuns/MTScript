import json
import os

from .base import BaseExchange


class BcexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'BCEX'
        self.exchange_id = 1339
        self.base_url = 'https://www.bcex.ca/api_market/getinfo_btc'

        self.ticker_url = '/coin'

        self.alias = 'BCEX'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pair(self):
        conf_path = os.path.abspath(os.path.dirname(__file__)) +\
                    '/exchange_conf/bcex.json'
        with open(conf_path, 'r') as f:
            data = json.load(f)

        return data

    def get_remote_data(self):
        return_data = []
        pairs = self.get_available_pair()['pairs']
        for i, p in enumerate(pairs, 1):
            print('dealing {}/{} pair: {}'.format(i, len(pairs), p))
            try:
                (symbol, anchor) = p.split('_')
                url = '{}{}/{}'.format(self.base_url,
                                       self.ticker_url,
                                       str(symbol).lower())
                # print(url)
                r = self.get_json_request(url)
                if symbol.lower() == 'ans':
                    symbol = 'NEO'
                price = float(r['price'])
                volume = float(r['volume_24h'])

                data = {
                    'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                    'price': price,
                    'volume': volume,
                    'volume_anchor': price * volume
                }

                return_data.append(data)
            except Exception as e:
                print('error happened, exist {}: {}'.format(p, e))
        return return_data
