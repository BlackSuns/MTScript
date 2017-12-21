import os

from .base import BaseExchange


class LbankExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'lbank'
        self.exchange_id = 1369
        self.base_url = 'http://api.lbank.info/v1'

        self.ticker_url = '/ticker.do?symbol=all'

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

        for i in result:
            (symbol, anchor) = i['symbol'].split('_')
            if symbol and anchor:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                price = float(i['ticker']['latest'])
                volume = float(i['ticker']['vol'])
                volume_anchor = float(i['ticker']['turnover'])
                return_data.append({
                    'pair': pair,
                    'price': price,
                    'volume_anchor': volume_anchor,
                    'volume': volume,
                })

        # print(return_data)
        return return_data
