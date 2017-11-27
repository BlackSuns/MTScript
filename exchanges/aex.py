import os

from .base import BaseExchange


class AexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'aex'
        self.exchange_id = 1351
        self.base_url = 'https://www.aex.com'
        # https://coding.net/u/byoneself/p/cex_api/git/blob/master/cex_api.md

        self.ticker_url = '/httpAPIv2.php'

        self.alias = 'aex'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []
        pairs = []

        for k in result.keys():
            if  '_' not in k:
                pairs.append(k)

        for p in pairs:
            (symbol, anchor) = p.split('2')
            return_data.append({
                'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                'price': float(pairs[p]),
                'volume': float(pairs['{}_amo'.format(p)]),
                'volume_anchor': float(pairs['{}_vol'.format(p)])
            })


        # print(return_data)
        return return_data
