import json
import os
from .base import BaseExchange


class CexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'cex'
        self.exchange_id = 1353
        self.base_url = 'http://api.cex.com/api/v1'

        self.ticker_url = '/ticker.do'

        self.alias = 'cex'
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
        for i, p in enumerate(pairs, 1):
            print('dealing {}/{} pair: {}'.format(i, len(pairs), p))
            try:
                url = '{}{}?symbol={}'.format(self.base_url,
                                              self.ticker_url,
                                              str(p).lower())
                # print(url)
                r = self.get_json_request(url)
                price = float(r['ticker']['last'])
                volume = float(r['ticker']['vol']) if 'vol' in r['ticker'].keys() else 0

                data = {
                    'pair': str(p).replace('_', '/').upper(),
                    'price': price,
                    'volume': volume,
                    'volume_anchor': price * volume
                }

                return_data.append(data)
            except Exception as e:
                print('error happened, exist {}: {}'.format(p, e))
        return return_data
