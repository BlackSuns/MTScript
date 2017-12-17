import json
import os

from .base import BaseExchange


class CoinwExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'coinw'
        self.exchange_id = 1376
        self.base_url = 'https://www.coinw.com/appApi.html'

        self.ticker_url = '?action=market'

        self.alias = ''
        self.with_name = True
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pairs(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data

    def get_remote_data(self):
        return_data = []
        anchor = 'CNY'
        pairs = self.get_available_pairs()

        for k in pairs.keys():
            try:
                url = '{}{}&symbol={}'.format(self.base_url, self.ticker_url, k)
                result = self.get_json_request(url)

                return_data.append({
                    'name': pairs[k][1],
                    'pair': '{}/{}'.format(pairs[k][0].upper(), anchor),
                    'price': result['data']['last'],
                    'volume': result['vol'],
                    'volume_anchor': result['data']['last'] * result['vol']
                })
            except Exception as e:
                print(e)

        return return_data
