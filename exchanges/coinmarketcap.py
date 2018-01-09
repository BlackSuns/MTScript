import json
import os

from .base import BaseExchange


class CmcExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'cmc'
        self.exchange_id = 1303
        self.base_url = 'https://api.coinmarketcap.com/v1'

        self.ticker_url = '/ticker/?convert=CNY&limit=3000'

        self.alias = 'cmc'
        self.with_name = True
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_mytoken_list(self):
        with open(self.exchange_conf, 'r') as f:
            data = json.load(f)

        self.my_data = data['supply']

    def get_remote_data(self):
        self.get_mytoken_list()
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for i in result:
            # print(i)
            name = i['name']
            symbol = i['symbol']
            if name == 'IOTA' and symbol == 'MIOTA':
                symbol = 'IOT'
            anchor = 'CNY'
            rank = int(i['rank'])
            price = float(i['price_cny']) if i['price_cny'] else 0
            volume_anchor = \
                float(i['24h_volume_cny']) if i['24h_volume_cny'] else 0
            percent_change_24h = \
                float(i['percent_change_24h']) if i['percent_change_24h']\
                else 0
            market_cap_usd = \
                float(i['market_cap_usd']) if i['market_cap_usd']\
                else 0
            available_supply = \
                float(i['available_supply']) if i['available_supply']\
                else 0
            total_supply = \
                float(i['total_supply']) if i['total_supply']\
                else 0
            max_supply = \
                float(i['max_supply']) if i['max_supply']\
                else 0


            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                rd = {
                    'name': name,
                    'pair': pair,
                    # 'price': price,
                    'volume_anchor': volume_anchor,
                    'volume': volume_anchor / price if price else 0,
                    # 'rank': rank,
                    # 'percent_change_24h': percent_change_24h,
                    # 'market_cap_usd': market_cap_usd,
                    'available_supply': available_supply,
                    'total_supply': total_supply,
                    'max_supply': max_supply
                }

                mt_key = '{}/{}'.format(name, symbol)
                if mt_key in self.my_data.keys():
                    if self.my_data[mt_key]['force']:
                        rd['available_supply'] = self.my_data[mt_key].get('available', 0)
                        rd["total_supply"] = self.my_data[mt_key].get('total', 0)
                        rd["max_supply"] = self.my_data[mt_key].get('max', 0)
                    else:
                        if rd['available_supply'] == 0:
                            rd['available_supply'] = self.my_data[mt_key].get('available', 0)
                        if rd['total_supply'] == 0:
                            rd['total_supply'] = self.my_data[mt_key].get('total', 0)
                        if rd['max_supply'] == 0:
                            rd['max_supply'] = self.my_data[mt_key].get('max', 0)

                return_data.append(rd)

        # print(return_data)
        return return_data
