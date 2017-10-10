from .base import BaseExchange


class HuobiExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        # https://github.com/huobiapi/API_Docs/wiki/REST_api_reference
        self.exchange = 'huobi'
        self.exchange_id = 108
        self.base_url = 'https://api.huobi.pro'

        self.ticker_url = '/market/detail/merged'

        self.alias = '火币'

    def get_remote_data(self):
        return_data = []
        symbols = ('ethbtc', 'ltcbtc', 'etcbtc', 'bccbtc')
        for s in symbols:
            url = '{}{}?symbol={}'.format(
                self.base_url,
                self.ticker_url,
                s)
            print(url)
            r = self.get_json_request(url)
            return_data.append(
                {
                    'pair': '{}/BTC'.format(s[:-3].upper()),
                    'price': r['tick']['close'],
                    'volume': r['tick']['amount'],
                    'volume_anchor': r['tick']['vol'],
                })

        return return_data
