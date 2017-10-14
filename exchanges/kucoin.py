from .base import BaseExchange


class KucoinExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'KuCoin'
        self.exchange_id = 1337
        self.base_url = 'https://api.kucoin.com/v1/market/open'

        self.ticker_url = '/symbols'

        self.alias = '酷币'

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for i in result['data']:
            if i['trading']:
                (symbol, anchor) = str(i['symbol']).split('-')
                if anchor and symbol:
                    pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                    return_data.append({
                        'pair': pair,
                        'price': i['lastDealPrice'],
                        'volume_anchor': i['volValue'],
                        'volume': i['vol'],
                    })

        # print(return_data)
        return return_data
