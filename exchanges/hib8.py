import os

from .base import BaseExchange


class Hib8Exchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'hib8'
        self.exchange_id = 1375
        self.base_url = 'https://www.hib8.com/api'

        self.ticker_url = '/coinlist'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        # print(result)
        return_data = []

        for i in result:
            (symbol, anchor) = str(i['symbol']).split('-')
            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                price = i['last'] if i['last'] else 0
                volume = float(i['vol']) if i['vol'] else 0
                return_data.append({
                    'pair': pair,
                    'price': price,
                    'volume_anchor': price * volume,
                    'volume': volume,
                })

        # print(return_data)
        return return_data
