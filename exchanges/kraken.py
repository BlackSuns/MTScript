import os

from .base import BaseExchange


class KrakenExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'Kraken'
        self.exchange_id = 114
        self.base_url = 'https://api.kraken.com/0/public'

        self.pair_url = '/AssetPairs'
        self.ticker_url = '/Ticker'

        self.alias = 'Kraken'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    # get all available_pairs
    # update result to self.support_pairs
    # self.support_pairs is a list
    def get_available_pair(self):
        url = '{}{}'.format(self.base_url, self.pair_url)
        self.pair_callback(self.get_json_request(url))

    def pair_callback(self, result):
        self.support_pairs = []
        for k in result['result'].keys():
            self.support_pairs.append(k)

    def get_remote_data(self):
        self.get_available_pair()
        query_string = ','.join(self.support_pairs)
        url = '{}{}?pair={}'.format(
            self.base_url, self.ticker_url, query_string)
        # print(url)
        r = self.get_json_request(url)

        if r:
            return_data = []
            anchors = ('XBT', 'USD', 'EUR', 'ETH', 'JPY')

            for k in r['result']:
                symbol = k[:-3].upper()
                anchor = k[-3:].upper()
                if anchor in anchors:
                    if anchor == 'XBT':
                        anchor = 'BTC'
                    if len(symbol) >= 5\
                       and symbol[0] == 'X'\
                       and symbol[-1] in ('X', 'Z'):
                        symbol = symbol[1:-1]
                    if str(symbol).startswith("USDT"):
                        symbol = 'USDT'
                    if symbol == 'XBT':
                        symbol = 'BTC'

                    volume = float(r['result'][k]['v'][1])
                    avg_price = float(r['result'][k]['p'][1])
                    return_data.append(
                        {
                            'pair': '{}/{}'.format(symbol, anchor),
                            'price': float(r['result'][k]['c'][0]),
                            'volume': volume,
                            'volume_anchor': volume * avg_price,
                        }
                    )

            # print(return_data)
            return return_data
