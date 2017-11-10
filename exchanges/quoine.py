import os

from .base import BaseExchange


class QuoineExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'quoine'
        self.exchange_id = 21
        self.base_url = 'https://api.quoine.com'

        self.ticker_url = '/products'

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

        for t in result:
            try:
                symbol = t['base_currency']
                anchor = t['quoted_currency']
                price = float(t['last_traded_price'])
                volume = float(t['volume_24h'])
                avg_price = float(t['last_price_24h'])

                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': price,
                    'volume_anchor': avg_price * volume,
                    'volume': volume,
                })
            except Exception as e:
                print(e)

        # print(return_data)
        return return_data
