import os

from .base import BaseExchange


class Coin900Exchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'coin900'
        self.exchange_id = 1372
        self.base_url = 'https://coin900.com/apiv2'

        self.ticker_url = '/tickers'

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
        anchors = ('btc', 'eth', 'cxc')

        for k in result.keys():
            for anchor in anchors:
                if str(k).endswith(anchor):
                    symbol = str(k)[:-len(anchor)]
                    pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                    price = float(result[k]['last'])
                    volume = float(result[k]['volume'])

                    return_data.append({
                        'pair': pair,
                        'price': price,
                        'volume_anchor': price * volume,
                        'volume': volume,
                    })


        # print(return_data)
        return return_data
