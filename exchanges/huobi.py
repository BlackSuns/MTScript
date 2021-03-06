# import json
import os

from .base import BaseExchange


class HuobiExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        # https://github.com/huobiapi/API_Docs/wiki/REST_api_reference
        self.exchange = 'huobi'
        self.exchange_id = 108
        self.base_url = 'https://api.huobi.pro'

        self.ticker_url = '/market/detail/merged'
        self.pair_url = '/v1/common/symbols'

        self.alias = '火币'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    # def get_available_pair(self):
    #     with open(self.exchange_conf, 'r') as f:
    #         data = json.load(f)

    #     return list(data['pairs'])
    def get_available_pair(self):
        url = '{}{}'.format(self.base_url, self.pair_url)
        # print(url)
        r = self.get_json_request(url)
        pairs = []

        for p in r['data']:
            pairs.append('{}_{}'.format(p['base-currency'], p['quote-currency']))

        return pairs


    def get_remote_data(self):
        return_data = []
        pairs = self.get_available_pair()
        # print(pairs)
        for p in pairs:
            (symbol, anchor) = str(p).split('_')
            url = '{}{}?symbol={}{}'.format(
                self.base_url,
                self.ticker_url,
                symbol,
                anchor)
            print(url)

            try:
                r = self.get_json_request(url)
                return_data.append(
                    {
                        'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                        'price': r['tick']['close'],
                        'volume': r['tick']['amount'],
                        'volume_anchor': r['tick']['vol'],
                    })
            except Exception as e:
                print(e)

        return return_data
