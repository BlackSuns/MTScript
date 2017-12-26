import os

from .base import BaseExchange


class AsdbiExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'asdbi'
        self.exchange_id = 1390
        self.base_url = 'https://www.asdbi.com/interfaces'

        self.ticker_url = '/trade/homevcoin'

        self.alias = '什币网'
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
        anchor = 'CNY'

        for p in result:
            symbol = p['unit']
            pair = '{}/{}'.format(symbol.upper(), anchor.upper())
            return_data.append({
                'pair': pair,
                'price': p['price'],
                'volume_anchor': p['trademoney24hour'],
                'volume': p['tradecount24hour'],
            })

        # print(return_data)
        return return_data
