import os

from .base import BaseExchange


class AllcoinExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'allcoin'
        self.exchange_id = 41
        self.base_url = 'https://www.allcoin.com/Home'

        self.ticker_url = '/MarketOverViewDetail/'

        self.alias = 'Allcoin'
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        return_data = []
        url = '{}{}'.format(self.base_url, self.ticker_url)
        r = self.get_json_request(url)
        # print(r)

        for market in r['marketCoins']:
            for m in market['Markets']:
                return_data.append({
                    'pair': '{}/{}'.format(m['Market']['Primary'].upper(), m['Market']['Secondary'].upper()),
                    'price': float(m['LastPrice']),
                    'volume': float(m['Volumn24H']),
                    'volume_anchor': float(m['Amount24H'])
                })

        return return_data
