import os

from .base import BaseExchange


class CoincheckExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'coincheck'
        self.exchange_id = 149
        self.base_url = 'https://coincheck.com/api'

        self.ticker_url = '/ticker'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        try:
            symbol = 'BTC'
            anchor = 'JPY'
            price = result['last']
            volume = result['volume']

            pair = '{}/{}'.format(symbol.upper(), anchor.upper())
            return_data.append({
                'pair': pair,
                'price': price,
                'volume_anchor': price * volume,
                'volume': volume,
            })
        except Exception as e:
            print(e)

        # print(return_data)
        return return_data
