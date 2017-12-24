import os

from .base import BaseExchange


class KkexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'kkex'
        self.exchange_id = 1388
        self.base_url = 'https://kkex.com/api/v1'

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
        # print(result)
        return_data = []
        anchors = ("BTC",)

        for i in result['tickers']:
            for k in i.keys():
                for anchor in anchors:
                    if str(k).endswith(anchor):
                        symbol = k[:-len(anchor)]
                        pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                        price = float(i[k]['last'])
                        volume = float(i[k]['vol'])

                        return_data.append({
                            'pair': pair,
                            'price': price,
                            'volume_anchor': price * volume,
                            'volume': volume,
                        })

        # print(return_data)
        return return_data
