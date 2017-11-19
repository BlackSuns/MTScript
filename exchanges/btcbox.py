import json
import os

from .base import BaseExchange


class BtcboxExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'btcbox'
        self.exchange_id = 28
        self.base_url = 'https://www.btcbox.co.jp/api/v1'

        self.ticker_url = '/ticker'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pair(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data

    def get_remote_data(self):
        return_data = []
        anchor = 'JPY'
        symbols = self.get_available_pair()['name_symbol']
        for i, symbol in enumerate(symbols.keys(), 1):
            print('dealing {}/{} symbol: {}'.format(i, len(symbols), symbol))
            try:
                url = '{}{}?coin={}'.format(self.base_url,
                                            self.ticker_url,
                                            str(symbol).lower())
                # print(url)
                r = self.get_json_request(url)

                data = {
                    'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                    'price': r['last'],
                    'volume': r['vol'],
                    'volume_anchor': r['last'] * r['vol']
                }

                return_data.append(data)
            except Exception as e:
                print('error happened, exist {}: {}'.format(p, e))
        return return_data
