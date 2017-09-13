from .base import BaseExchange


class CCexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'C-CEX'
        self.exchange_id = 10
        self.base_url = 'https://c-cex.com'

        self.ticker_url = '/t/api_pub.html?a=getmarketsummaries'

        self.alias = 'C-CEX'

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for i in result['result']:
            (symbol, anchor) = str(i['MarketName']).split('-')
            if anchor and symbol and symbol not in ('USD', 'EUR'):
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'pair': pair,
                    'price': i['Last'],
                    'volume_anchor': i['BaseVolume'],
                    'volume': i['Volume'],
                })

        # print(return_data)
        return return_data
