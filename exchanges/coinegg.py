import json
import re
import os

from .base import BaseExchange


class CoineggExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'coinegg'
        self.exchange_id = 1346
        self.base_url = 'https://api.coinegg.com/api/v1'

        self.ticker_url = '/allticker'

        self.alias = 'COINEGG'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []
        anchor = 'BTC'

        for s in result.keys():
            pair = '{}/{}'.format(s.upper(), anchor)
            return_data.append({
                'pair': pair,
                'price': float(result[s]['last']),
                'volume_anchor': float(result[s]['volume']),
                'volume': float(result[s]['vol']),
            })

        # print(return_data)
        return return_data
