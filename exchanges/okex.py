import json
import os
from .base import BaseExchange


class OkexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        # https://www.okex.com/rest_api.html
        self.exchange = 'okex'
        self.exchange_id = 1324
        self.base_url = 'https://www.okex.com/api/v1'

        self.ticker_url = '/ticker.do'

        self.alias = 'okex'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_pair(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return list(data['pairs'])

    def get_remote_data(self):
        return_data = []
        pairs = self.get_available_pair()

        for p in pairs:
            url = '{}{}?symbol={}'.format(
                self.base_url,
                self.ticker_url,
                p)
            print(url)

            try:
                r = self.get_json_request(url)
                (symbol, anchor) = p.split('_')
                price = float(r['ticker']['last'])
                volume = float(r['ticker']['vol'])
                return_data.append(
                    {
                        'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                        'price': price,
                        'volume': volume,
                        'volume_anchor': price * volume,
                    })
            except Exception as e:
                print(e)

        return return_data
