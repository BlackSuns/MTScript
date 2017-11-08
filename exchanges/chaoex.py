import os

from .base import BaseExchange


class ChaoexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'chaoex'
        self.exchange_id = 1338
        self.base_url = 'https://www.chaoex.com/12lian'

        self.ticker_url = '/quote/realTime'
        self.pair_url = '/coin/allCurrencyRelations'

        self.alias = '12链 Chaoex'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pairs(self):
        self.available_pairs = []
        url = '{}{}'.format(self.base_url, self.pair_url)
        pairs = self.get_json_request(url)['attachment']
        for pair in pairs:
            self.available_pairs.append({
                'symbol': pair['tradeCurrencyNameEn'],
                'symbol_id': pair['tradeCurrencyId'],
                'anchor': pair['baseCurrencyNameEn'],
                'anchor_id': pair['baseCurrencyId'],
            })

    def get_remote_data(self):
        return_data = []
        self.get_available_pairs()
        for p in self.available_pairs:
            try:
                url = '{}{}?tradeCurrencyId={}&baseCurrencyId={}'.format(
                    self.base_url, self.ticker_url,
                    p['symbol_id'],
                    p['anchor_id'])
                print(url)
                data = self.ticker_callback(self.get_json_request(url))
                data['pair'] = '{}/{}'.format(p['symbol'].upper(), p['anchor'].upper())
                return_data.append(data)
            except Exception as e:
                print(e)
        return return_data

    def ticker_callback(self, result):
        price = float(result['attachment']['last'])
        volume = float(result['attachment']['vol'])
        return {
            'price': price,
            'volume': volume,
            'volume_anchor': price * volume,
        }
