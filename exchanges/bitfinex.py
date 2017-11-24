import os

from .base import BaseExchange


class BitfinexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bitfinex'
        self.exchange_id = 126
        self.base_url = 'https://api.bitfinex.com/v2'

        self.pair_url = 'https://api.bitfinex.com/v1/symbols_details'
        self.ticker_url = '/tickers'

        self.alias = 'bitfinex'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    # get all available_pairs
    # update result to self.support_pairs
    # self.support_pairs is a list
    def get_available_pair(self):
        self.pair_callback(self.get_json_request(self.pair_url))

    def pair_callback(self, result):
        self.support_pairs = []
        for r in result:
            self.support_pairs.append('t{}'.format(r['pair'].upper()))

    def get_remote_data(self):
        self.get_available_pair()
        request_url = '{}{}?symbols={}'.format(self.base_url, self.ticker_url, ','.join(self.support_pairs))
        return self.ticker_callback(self.get_json_request(request_url))

    def ticker_callback(self, result):
        return_data = []
        anchors = ('USD', 'BTC', 'ETH', 'EUR')

        for r in result:
            pair = r[0][1:]
            for anchor in anchors:
                if str(pair).endswith(anchor):
                    symbol = pair[:-len(anchor)]
                    price = r[7]
                    volume = r[8]
                    return_data.append({
                        'pair': '{}/{}'.format(symbol, anchor),
                        'price':    price,
                        'volume':   volume,
                        "volume_anchor":    price * volume
                        })
                    break

        return return_data
