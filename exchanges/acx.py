import os

from .base import BaseExchange


class AcxExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'acx'
        self.exchange_id = 1318
        self.base_url = 'https://acx.io/api/v2'

        self.ticker_url = '/tickers.json'

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

        for k in result.keys():
            price = float(result[k]['ticker']['last'])
            volume = float(result[k]['ticker']['vol'])
            return_data.append({
                'pair': result[k]['name'],
                'price': price,
                'volume_anchor': price * volume,
                'volume': volume,
            })

        # print(return_data)
        return return_data
