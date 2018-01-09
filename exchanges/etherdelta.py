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
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_available_symbol(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data['name_symbol']

    def get_whitelist(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        return data['sc_whitelist'] if 'sc_whitelist' in data.keys() else []

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l.
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def get_remote_data(self):
        return_data = []
        whitelist = self.get_whitelist()
        available_pairs = self.get_available_symbol()
        symbol_count = 50
        parts = self.chunks(list(available_pairs.keys()), symbol_count)

        # start dealing addr pair
        l = list(whitelist.keys())
        fsyms = ','.join(l)
        url = '{}{}'.format(
                    self.base_url, self.ticker_url)
        url = '{}?fsyms={}&tsyms=ETH&e=EtherDelta'.format(url, fsyms)
        r = self.get_json_request(url)
        for d in r['RAW'].keys():
            symbol = whitelist[d]
            anchor = 'ETH'
            pair = '{}/{}'.format(symbol.upper(), anchor.upper())
            return_data.append({
                'pair': pair,
                'price': r['RAW'][d]['ETH']['PRICE'],
                'volume_anchor': r['RAW'][d]['ETH']['VOLUME24HOURTO'],
                'volume': r['RAW'][d]['ETH']['VOLUME24HOUR']
            })

        print('ADDR PAIR DONE...')

        # start dealing symbol pair
        for p in parts:
            # print(p)
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
            if result[i]['ETH']['LASTVOLUME'] * result[i]['ETH']['PRICE'] > 0.005:
                symbol = i
                anchor = 'ETH'

                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': result[i]['ETH']['PRICE'],
                    'volume_anchor': result[i]['ETH']['TOTALVOLUME24HTO'],
                    'volume': result[i]['ETH']['TOTALVOLUME24H'],
                })

        # print(return_data)
        return return_data
