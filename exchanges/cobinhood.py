import os

from .base import BaseExchange


class CobinhoodExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'cobinhood'
        self.exchange_id = 1395
        self.base_url = 'https://api.cobinhood.com/v1'

        self.pair_url = '/market/stats'
        self.ticker_url = '/market/tickers'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pairs(self):
        pairs = []
        url = '{}{}'.format(self.base_url, self.pair_url)
        # print(url)
        r = self.get_json_request(url)
        for p in r['result'].keys():
            pairs.append(p)

        return pairs

    def get_remote_data(self):
        return_data = []
        pairs = self.get_available_pairs()

        for p in pairs:
            url = '{}{}/{}'.format(self.base_url, self.ticker_url, p)
            r = self.get_json_request(url)
            (symbol, anchor) = p.split('-')
            pair = '{}/{}'.format(symbol, anchor)
            price = float(r['result']['ticker']['last_trade_price'])
            volume = float(r['result']['ticker']['24h_volume'])
            return_data.append({
                "pair": pair,
                "price": price,
                "volume": volume,
                "volume_anchor": price * volume,
            })

        return return_data
