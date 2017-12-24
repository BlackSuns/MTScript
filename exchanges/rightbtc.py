import os

from .base import BaseExchange


class RightbtcExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'rightbtc'
        self.exchange_id = 1380
        self.base_url = 'https://www.rightbtc.com/api/public'

        self.ticker_url = '/tickers'

        self.alias = ''
        self.with_name = False
        self.exchange_conf = os.path.abspath(os.path.dirname(__file__)) +\
            '/exchange_conf/{}.json'.format(self.exchange)

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        # print(result)
        return_data = []
        anchors = ('BTC', "ETH", "ETP")
        ratio = 0.00000001

        for i in result['result']:
            for anchor in anchors:
                if str(i['market']).endswith(anchor):
                    symbol = i['market'][:-len(anchor)]
                    pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                    price = int(i['last']) * ratio
                    avgprice = int(i['last24h']) * ratio
                    volume = int(i['vol24h']) * ratio

                    return_data.append({
                        'pair': pair,
                        'price': price ,
                        'volume_anchor': volume * avgprice,
                        'volume': volume,
                    })
                    break

        # print(return_data)
        return return_data
