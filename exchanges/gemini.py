import os

from .base import BaseExchange


class GeminiExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'gemini'
        self.exchange_id = 24
        self.base_url = 'https://api.gemini.com/v1'

        self.pair_url = '/symbols'
        self.ticker_url = '/pubticker'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    # get all available_pairs
    # update result to self.support_pairs
    # self.support_pairs is a list
    def get_available_pair(self):
        url = '{}{}'.format(self.base_url, self.pair_url)
        self.pair_callback(self.get_json_request(url))

    def pair_callback(self, result):
        # self.update_time = result['server_time']
        self.support_pairs = []
        for r in result:
            self.support_pairs.append(r)

    def get_remote_data(self):
        self.get_available_pair()
        anchors = ('usd', 'btc')
        return_data = []

        for p in self.support_pairs:
            for anchor in anchors:
                if str(p).endswith(anchor):
                    symbol = str(p)[:-len(anchor)]

                    url = '{}{}/{}'.format(
                        self.base_url, self.ticker_url, p)
                    res = self.get_json_request(url)
                    return_data.append({
                        'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                        'price': float(res['last']),
                        'volume': float(res['volume'][symbol.upper()]),
                        'volume_anchor': float(res['volume'][anchor.upper()]),
                    })
                    break

        return return_data
