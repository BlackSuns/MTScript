import os
from .base import BaseExchange


class CryptopiaExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'cryptopia'
        self.exchange_id = 40
        self.base_url = 'https://www.cryptopia.co.nz/api'

        self.ticker_url = '/GetMarkets'

        self.alias = 'Cryptopia'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for i in result['Data']:
            return_data.append({
                'pair': i["Label"],
                'price': i['LastPrice'],
                'volume_anchor': i['BaseVolume'],
                'volume': i['Volume'],
            })

        # print(return_data)
        return return_data
