import os

from .base import BaseExchange


class BxinthExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bxinth'
        self.exchange_id = 51
        self.base_url = 'https://bx.in.th/api'

        self.ticker_url = '/'

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
            symbol = result[k]['secondary_currency']
            anchor = result[k]['primary_currency']
            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': result[k]['last_price'],
                    'volume_anchor': result[k]['last_price'] * result[k]['volume_24hours'],
                    'volume': result[k]['volume_24hours'],
                })

        # print(return_data)
        return return_data
