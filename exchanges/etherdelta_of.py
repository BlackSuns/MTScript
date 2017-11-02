import json
import os

from .base import BaseExchange


class EtherdeltaExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'etherdelta'
        self.exchange_id = 34
        self.base_url = 'https://api.etherdelta.com'

        self.ticker_url = '/returnTicker'

        self.alias = 'EtherDelta'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def get_whitelist(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data['sc_whitelist'] if 'sc_whitelist' in data.keys() else []

    def ticker_callback(self, result):
        return_data = []
        whitelist = self.get_whitelist()
        # print(whitelist)

        total = len(result)
        curr = 0
        for k in result.keys():
            curr = curr + 1
            if result[k]['last']:
                (anchor, symbol) = str(k).split('_')
                if not str(symbol).startswith('0x') or symbol in whitelist:
                    ask = result[k]['ask']
                    last = result[k]['last']
                    percentChange = result[k]['percentChange']
                    rate = round(last/ask, 2) if ask else 0
                    print('{}/{} {}: rate is {}, last: {} ask: {} perc: {}'.format(curr, total, k, rate, last, ask, percentChange))
                    if anchor and symbol:
                        pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                        return_data.append({
                            'pair': pair,
                            'price': result[k]['last'],
                            'volume_anchor': result[k]['baseVolume'],
                            'volume': result[k]['quoteVolume'],
                        })

        return return_data
