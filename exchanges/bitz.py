import os

from .base import BaseExchange


class BitzExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'Bit-Z'
        self.exchange_id = 1321
        self.base_url = 'https://www.bit-z.com'

        self.ticker_url = '/api_v1/tickerall'

        self.alias = 'Bit-Z'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        if result['code'] == 0:
            for i in result['data'].keys():
                (symbol, anchor) = str(i).split('_')
                if anchor and symbol:
                    pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                    price = float(result['data'][i]['last'])
                    volume = float(result['data'][i]['vol'])
                    return_data.append({
                        'pair': pair,
                        'price': price,
                        'volume_anchor': price * volume,
                        'volume': volume,
                    })

        # print(return_data)
        return return_data
