import os

from .base import BaseExchange


class HksyExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'hksy'
        self.exchange_id = 1364
        self.base_url = 'https://api.hksy.com/pc/coinMarket/v1'

        self.ticker_url = '/selectCoinMarket?payCoinName=HKD'

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
        anchor = "HKD"

        for p in result['model']:
            symbol = p['defaultcnname']

            pair = '{}/{}'.format(symbol.upper(), anchor.upper())
            return_data.append({
                'pair': pair,
                'price': p['newclinchprice'],
                'volume_anchor': p['money24'],
                'volume': p['count24'],
            })

        # print(return_data)
        return return_data
