import json
import re
import os

from .base import BaseExchange


class BitfinexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bitfinex'
        self.exchange_id = 126
        self.base_url = 'https://min-api.cryptocompare.com'

        self.ticker_url = '/data/pricemultifull'

        self.alias = 'bitfinex'

    def get_available_symbol(self):
        conf_path = os.path.abspath(os.path.dirname(__file__)) +\
                    '/exchange_conf/bitfinex.json'
        with open(conf_path, 'r') as f:
            data = json.load(f)

        return data

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l.
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def get_remote_data(self):
        return_data = []
        anchors = ('USD', 'BTC', 'ETH')
        conf_data = self.get_available_symbol()
        for a in anchors:
            p = conf_data[a]
            fsyms = ','.join(p)
            url = '{}{}'.format(self.base_url, self.ticker_url)
            url = '{}?fsyms={}&tsyms={}&e=Bitfinex'.format(url, fsyms, a)
            # print(url)
            r = self.get_json_request(url)
            if 'Response' in r.keys() and r['Response'] == 'Error':
                try:
                    pattern = re.compile(r'(\w*-\w*)')
                    m = pattern.search(r['Message'])
                    if m:
                        symbol = m.group().split('-')[0]
                        p.remove(symbol)
                        print('removed symbol: {}'.format(symbol))
                except Exception as e:
                    print(e)
            else:
                return_data += self.ticker_callback(r['RAW'], a)
        return return_data

    def ticker_callback(self, result, anchor):
        return_data = []

        for i in result.keys():
            symbol = i

            pair = '{}/{}'.format(symbol.upper(), anchor.upper())
            return_data.append({
                'pair': pair,
                'price': result[i][anchor]['PRICE'],
                'volume_anchor': result[i][anchor]['VOLUME24HOURTO'],
                'volume': result[i][anchor]['VOLUME24HOUR'],
            })

        # print(return_data)
        return return_data
