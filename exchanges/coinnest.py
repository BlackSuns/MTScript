import json
import os

from .base import BaseExchange


class CoinnestExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'Coinnest'
        self.exchange_id = 1340
        self.base_url = 'https://api.coinnest.co.kr/api/pub'

        self.ticker_url = '/ticker'

        self.alias = 'Coinnest'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pair(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data

    def get_remote_data(self):
        return_data = []
        pairs = self.get_available_pair()['pairs']
        for i, p in enumerate(pairs, 1):
            print('dealing {}/{} pair: {}'.format(i, len(pairs), p))
            try:
                (symbol, anchor) = p.split('_')
                url = '{}{}?coin={}'.format(self.base_url,
                                            self.ticker_url,
                                            str(symbol).lower())
                # print(url)
                r = self.get_json_request(url)
                price = float(r['last'])
                volume = float(r['vol'])

                data = {
                    'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                    'price': price,
                    'volume': volume,
                    'volume_anchor': price * volume
                }

                return_data.append(data)
            except aException as e:
                print('error happened, exist {}: {}'.format(p, e))
        return return_data
