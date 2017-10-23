import os

from .base import BaseExchange


class BittrexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bittrex'
        self.exchange_id = 6
        self.base_url = 'https://bittrex.com/api/v1.1'

        self.ticker_url = '/public/getmarketsummaries'

        self.alias = 'bittrex'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for i in result['result']:
            (anchor, symbol) = str(i['MarketName']).split('-')
            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': i['Last'],
                    'volume_anchor': i['BaseVolume'],
                    'volume': i['Volume'],
                })

        # print(return_data)
        return return_data
