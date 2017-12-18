import os

from .base import BaseExchange


class BinanceExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'binance'
        self.exchange_id = 338
        self.base_url = 'https://api.binance.com/api/v1'

        self.ticker_url = '/ticker/24hr'

        self.alias = '币安'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []
        anchors = ('BTC', 'ETH', 'USDT', 'BNB')

        for i in result:
            pair = i['symbol']
            for anchor in anchors:
                if str(pair).endswith(anchor):
                    symbol = pair[:- len(anchor)]
                    pair = '{}/{}'.format(symbol.upper(), anchor.upper())

                    return_data.append({
                        'pair': pair,
                        'price': float(i['lastPrice']),
                        'volume_anchor': float(i['quoteVolume']),
                        'volume': float(i['volume']),
                    })

        # print(return_data)
        return return_data
