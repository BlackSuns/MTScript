from .base import BaseExchange


class BithumbExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bithumb'
        self.exchange_id = 68
        self.base_url = 'https://api.bithumb.com'

        self.ticker_url = '/public/ticker/ALL'

        self.alias = 'bithumb'

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        if result['status'] == "0000":
            for k in result['data'].keys():
                if isinstance(result['data'][k], dict):
                    symbol = k
                    anchor = 'KRW'
                    pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                    price = float(result['data'][k]['closing_price'])
                    volume = float(result['data'][k]['volume_1day'])
                    volume_anchor = volume * price
                    return_data.append({
                        'pair': pair,
                        'price': price,
                        'volume_anchor': volume_anchor,
                        'volume': volume,
                    })

        # print(return_data)
        return return_data
