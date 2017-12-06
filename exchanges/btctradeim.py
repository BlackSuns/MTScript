import os

from .base import BaseExchange


class BtctradeimExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'btctradeim'
        self.exchange_id = 1373
        self.base_url = 'http://api.btctrade.im/api/v1'

        self.ticker_url = '/ticker/region/'
        self.pair_url = 'https://www.btctrade.im/coin/{}/allcoin'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_symbols(self, url):
        self.get_json_request(url)

    def get_remote_data(self):
        anchors = ('btc', 'usc')
        return_data = []

        for anchor in anchors:
            symbol_url = self.pair_url.format(anchor)
            symbols = self.get_json_request(symbol_url).keys()

            for symbol in symbols:
                ticker_url = '{}{}/{}?coin={}'.format(self.base_url, self.ticker_url, anchor, symbol)
                result = self.get_json_request(ticker_url)
                return_data.append({
                    'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                    'price':  float(result['data']['last']),
                    'volume': float(result['data']['vol']),
                    'volume_anchor': float(result['data']['last']) * float(result['data']['vol'])
                })

        return return_data
