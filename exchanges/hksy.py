import json
import os

from .base import BaseExchange


class HksyExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'hksy'
        self.exchange_id = 1364
        self.base_url = 'http://openapi.hksy.com/app/coinMarket/v1'

        self.ticker_url = '/selectCoinMarketbyCoinName'

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
        symbol_map = {
            'NeoGas': 'GAS',
        }

        pairs = self.get_available_pair()['pairs']
        for i, p in enumerate(pairs, 1):
            print('dealing {}/{} pair: {}'.format(i, len(pairs), p))
            try:
                (symbol, anchor) = p.split('_')
                url = '{}{}?coinName={}&payCoinName={}'.format(self.base_url, self.ticker_url, symbol, anchor)
                # print(url)
                r = self.get_json_request(url)

                if symbol in symbol_map.keys():
                    symbol = symbol_map[symbol]

                data = {
                    'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                    'price': float(r["model"]["newclinchprice"]),
                    'volume':float(r["model"]["count24"]),
                    'volume_anchor': float(r["model"]["money24"])
                }

                return_data.append(data)
            except Exception as e:
                print('error happened, exist {}: {}'.format(p, e))
        return return_data
