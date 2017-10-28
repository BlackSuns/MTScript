import json
import re
import os

from .base import BaseExchange


class CoineggExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'coinegg'
        self.exchange_id = 1346
        self.base_url = 'https://api.coinegg.com/api/v1'

        self.ticker_url = '/ticker'

        self.alias = 'COINEGG'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_symbol(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data

    def get_remote_data(self):
        return_data = []
        anchor = 'BTC'
        conf_data = self.get_available_symbol()
        total = len(conf_data['name_symbol'])
        dealed = 1
        for k in conf_data['name_symbol'].keys():
            url = '{}{}?coin={}'.format(self.base_url,
                                        self.ticker_url,
                                        str(k).lower())

            print('dealing {}/{}: {}'.format(dealed, total, url))
            dealed += 1
            try:
                r = self.get_json_request(url)
                # print(r)
                price = float(r['last'])
                volume = float(r['vol'])

                data = {
                    'pair': '{}/{}'.format(k.upper(), anchor.upper()),
                    'price': price,
                    'volume': volume,
                    'volume_anchor': price * volume
                }

                return_data.append(data)
            except Exception as e:
                print('error happened, {}'.format(e))
        return return_data
