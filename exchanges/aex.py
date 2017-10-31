import os

from .base import BaseExchange


class AexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'aex'
        self.exchange_id = 1351
        self.base_url = 'http://api.aex.com'

        self.ticker_url = '/ticker.php?c=all&mk_type=btc'

        self.alias = 'aex'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url), 'BTC')

    def ticker_callback(self, result, anchor):
        return_data = []

        for i in result.keys():
            if result[i]['ticker']:
                symbol = i
                if anchor and symbol:
                    pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                    price = result[i]['ticker']['last']
                    vol = result[i]['ticker']['vol']

                    return_data.append({
                        'pair': pair,
                        'price': price,
                        'volume_anchor': price * vol,
                        'volume': vol,
                    })

        # print(return_data)
        return return_data
