import json
import re
import os

from .base import BaseExchange


class EtherdeltaExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'etherdelta'
        self.exchange_id = 34
        self.base_url = 'https://min-api.cryptocompare.com'

        self.ticker_url = '/data/pricemultifull'

        self.alias = 'EtherDelta'

    def get_available_symbol(self):
        conf_path = os.path.abspath(os.path.dirname(__file__)) +\
                    '/exchange_conf/etherdelta.json'
        with open(conf_path, 'r') as f:
            data = json.load(f)

        return data['symbols']

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l.
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def get_remote_data(self):
        return_data = []
        symbol_count = 50
        parts = self.chunks(self.get_available_symbol(), symbol_count)
        for p in parts:
            error_count = len(p)
            while True:
                url = '{}{}'.format(
                    self.base_url, self.ticker_url)
                error_count = error_count - 1
                # print(error_count)
                if error_count <= 0:
                    break

                fsyms = ','.join(p)
                url = '{}?fsyms={}&tsyms=ETH&e=EtherDelta'.format(url, fsyms)
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
                    return_data += self.ticker_callback(r['RAW'])
                    break
        return return_data

    def ticker_callback(self, result):
        return_data = []

        for i in result.keys():
            if result[i]['ETH']['LASTVOLUME'] > 0.01:
                symbol = i
                anchor = 'ETH'

                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': result[i]['ETH']['PRICE'],
                    'volume_anchor': result[i]['ETH']['VOLUME24HOURTO'],
                    'volume': result[i]['ETH']['VOLUME24HOUR'],
                })

        # print(return_data)
        return return_data
