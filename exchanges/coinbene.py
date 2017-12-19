import os

from .base import BaseExchange


class CoinbeneExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'coinbene'
        self.exchange_id = 1377
        self.base_url = 'http://www.coinbene.com/api'

        self.ticker_url = '/service/006-001'

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

        for p in result["dayPrices"]:
            price = float(p['nowPrice']) if p['nowPrice'] else 0
            volume = float(p['volume24']) if p['volume24'] else 0
            pair = p['name']
            if str(pair).endswith('BCNY'):
                pair = pair[:-4] + 'BitCNY'

            return_data.append({
                'pair': pair,
                'price': price,
                'volume_anchor': price * volume,
                'volume': volume,
            })

        # print(return_data)
        return return_data
