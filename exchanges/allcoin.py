import json
import os

from .base import BaseExchange


class AllcoinExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'allcoin'
        self.exchange_id = 41
        self.base_url = 'https://api.allcoin.com/api/v1'

        self.ticker_url = '/ticker'

        self.alias = 'Allcoin'
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
                url = '{}{}?symbol={}'.format(self.base_url, self.ticker_url, p)
                # print(url)
                r = self.get_json_request(url)

                data = {
                    'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                    'price': r['ticker']['last'],
                    'volume': r['ticker']['vol'],
                    'volume_anchor': r['ticker']['last'] * r['ticker']['vol']
                }

                return_data.append(data)
            except Exception as e:
                print('error happened, exist {}: {}'.format(p, e))
        return return_data
