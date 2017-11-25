import os

from .base import BaseExchange


class UncoinexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'uncoinex'
        self.exchange_id = 1367
        self.base_url = 'http://open.uncoinex.com/api/v1'

        self.ticker_url = '/ticker'

        self.alias = '澳洲U网'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for r in result:
            (symbol, anchor) = str(r['symbol']).split('_')
            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': float(r['price']),
                    'volume_anchor': float(r['amount']),
                    'volume': float(r['volume']),
                })

        # print(return_data)
        return return_data