import os
from .base import BaseExchange


class CoinoneExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'coinone'
        self.exchange_id = 35
        self.base_url = 'https://api.coinone.co.kr'

        self.ticker_url = '/ticker?currency=all'

        self.alias = 'coinone'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []
        exclude_keys = ('timestamp', 'result', 'errorCode')

        for k in result.keys():
            if k not in exclude_keys:
                symbol = k
                anchor = 'KRW'
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                price = float(result[k]['last'])
                volume = float(result[k]['volume'])
                volume_anchor = volume * price
                return_data.append({
                    'pair': pair,
                    'price': price,
                    'volume_anchor': volume_anchor,
                    'volume': volume,
                })

        # print(return_data)
        return return_data
