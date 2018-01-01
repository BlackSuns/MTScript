import json
import os
from .base import BaseExchange


class JexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'jex'
        self.exchange_id = 1394
        self.base_url = 'https://www.jex.com/api'

        self.ticker_url = '/klineData.do?marketFrom=0&type=0&limit=1440&symbol='

        self.alias = 'jex'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pair(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data

    def get_remote_data(self):
        return_data = []
        pairs = self.get_available_pair()['pairs']
        # print(pairs)
        for k in pairs.keys():
            try:
                url = '{}{}{}'.format(self.base_url,
                                      self.ticker_url,
                                      k)
                print(url)
                r = self.get_json_request(url)
                price = r[-1][2]
                volume = 0
                for t in r:
                    volume += t[-1]

                data = {
                    'pair': pairs[k],
                    'price': price,
                    'volume': volume,
                    'volume_anchor': price * volume
                }

                return_data.append(data)
            except Exception as e:
                print('error happened: {}'.format(e))
        return return_data
