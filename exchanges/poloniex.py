import os

from .base import BaseExchange


class PoloniexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'Poloniex'
        self.exchange_id = 100
        self.base_url = 'https://poloniex.com'

        self.ticker_url = '/public?command=returnTicker'

        self.alias = 'poloniex'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for i in result.keys():
            (anchor, symbol) = str(i).split('_')
            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': result[i]['last'],
                    'volume_anchor': result[i]['baseVolume'],
                    'volume': result[i]['quoteVolume'],
                })

        # print(return_data)
        return return_data
