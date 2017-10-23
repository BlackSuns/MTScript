import os

from .base import BaseExchange


class GateioExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'gateio'
        self.exchange_id = 1333
        self.base_url = 'http://data.gate.io/api2/1'

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
        return_data = []

        for k in result.keys():
            (symbol, anchor) = str(k).split('_')
            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': result[k]['last'],
                    'volume_anchor': result[k]['baseVolume'],
                    'volume': result[k]['quoteVolume'],
                })

        # print(return_data)
        return return_data
