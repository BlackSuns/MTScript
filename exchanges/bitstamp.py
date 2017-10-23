import os

from .base import BaseExchange


class BitstampExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'BitStamp'
        self.exchange_id = 101
        self.base_url = 'https://www.bitstamp.net/api/v2'

        self.ticker_url = '/ticker'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    # get all available_pairs
    # update result to self.support_pairs
    # self.support_pairs is a list
    def get_available_pair(self):
        return (
            'btcusd',
            'btceur',
            'xrpusd',
            'xrpeur',
            'xrpbtc',
            'ltcusd',
            'ltceur',
            'ltcbtc',
            'ethusd',
            'etheur',
            'ethbtc',
        )

    def get_remote_data(self):
        return_data = []
        pairs = self.get_available_pair()
        anchors = ('usd', 'eur', 'btc')
        for p in pairs:
            symbol = p[:-3]
            anchor = p[-3:]
            if anchor in anchors:
                url = '{}{}/{}/'.format(self.base_url,
                                        self.ticker_url,
                                        p)
                r = self.ticker_callback(self.get_json_request(url))
                if r:
                    r['pair'] = '{}/{}'.format(symbol.upper(), anchor.upper())
                    return_data.append(r)

        return return_data

    def ticker_callback(self, result):
        if 'last' in result.keys()\
           and 'volume' in result.keys()\
           and 'vwap' in result.keys():
            return {
                'price': result['last'],
                'volume': result['volume'],
                'volume_anchor': float(result['volume']) * float(result['vwap'])
            }
        else:
            return None
