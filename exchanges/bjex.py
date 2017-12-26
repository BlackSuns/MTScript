import os

from .base import BaseExchange


class BjexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bjex'
        self.exchange_id = 1389
        self.base_url = 'http://api.gogoico.cn/pc/coinMarket/v1/bjex'

        self.ticker_url = '/selectAllCoinMarket'

        self.alias = '币君'
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

        for anchor in result['model'].keys():
            for p in result['model'][anchor]:
                symbol = p['defaultenname']
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': p['newclinchprice'],
                    'volume_anchor': p['money24'],
                    'volume': p['count24'],
                })

        # print(return_data)
        return return_data
