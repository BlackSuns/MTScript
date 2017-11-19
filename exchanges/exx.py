import os

from .base import BaseExchange


class ExxExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'exx'
        self.exchange_id = 1363
        self.base_url = 'https://api.exx.com/data/v1'

        self.ticker_url = '/tickers'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        excludes = ['deth', 'dhsr', 'dqtum']
        return_data = []

        for k in result.keys():
            (symbol, anchor) = str(k).split('_')
            if anchor and symbol and symbol not in excludes:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                price = float(result[k]['last'])
                volume = float(result[k]['vol'])
                return_data.append({
                    'pair': pair,
                    'price': price,
                    'volume_anchor': price * volume,
                    'volume': volume,
                })

        # print(return_data)
        return return_data
