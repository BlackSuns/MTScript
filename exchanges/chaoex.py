import os

from .base import BaseExchange


class ChaoexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'Chaoex'
        self.exchange_id = 1338
        self.base_url = 'https://www.chaoex.com/12lian'

        self.ticker_url = '/quote/realTime'

        self.alias = '12链 Chaoex'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

        self.currency_ids = {
            'BTC': 1,
            'LTC': 2,
            'ETH': 3,
            'DLC': 4,
            'TLC': 5,
            'LSK': 6,
            'ARC': 7,
            'BXB': 8,
            'XAS': 9,
            'NULS': 10,
            'EXP': 11,
        }
        self.available_pairs = {
            'DLC/BTC': (4, 1),
            'LTC/BTC': (2, 1),
            'ETH/BTC': (3, 1),
            'TLC/BTC': (5, 1),
            'LSK/BTC': (6, 1),
            'XAS/BTC': (9, 1),
            'NULS/BTC': (10, 1),
            'LTC/ETH': (2, 3),
            'LSK/ETH': (6, 3),
            # 'ARC/DLC': (7, 4),
            # 'BXB/DLC': (8, 4),
            # 'EXP/DLC': (11, 4),
        }

    def get_remote_data(self):
        return_data = []
        for p in self.available_pairs.keys():
            url = '{}{}?tradeCurrencyId={}&baseCurrencyId={}'.format(
                self.base_url, self.ticker_url,
                self.available_pairs[p][0],
                self.available_pairs[p][1])
            # print(url)
            data = self.ticker_callback(self.get_json_request(url))
            data['pair'] = p
            return_data.append(data)
        return return_data

    def ticker_callback(self, result):
        price = float(result['attachment']['last'])
        volume = float(result['attachment']['vol'])
        return {
            'price': price,
            'volume': volume,
            'volume_anchor': price * volume,
        }
