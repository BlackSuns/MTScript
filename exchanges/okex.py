from .base import BaseExchange


class OkexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        # https://www.okex.com/rest_api.html
        self.exchange = 'okex'
        self.exchange_id = 1324
        self.base_url = 'https://www.okex.com/api/v1'

        self.ticker_url = '/ticker.do'

        self.alias = 'okex'

    def get_remote_data(self):
        return_data = []
        symbols = ('eth_btc', 'ltc_btc', 'etc_btc',
                   'bcc_btc', 'btc_usdt', 'eth_usdt')
        for s in symbols:
            url = '{}{}?symbol={}'.format(
                self.base_url,
                self.ticker_url,
                s)
            print(url)
            r = self.get_json_request(url)
            (symbol, anchor) = s.split('_')
            price = float(r['ticker']['last'])
            volume = float(r['ticker']['vol'])
            return_data.append(
                {
                    'pair': '{}/{}'.format(symbol.upper(), anchor.upper()),
                    'price': price,
                    'volume': volume,
                    'volume_anchor': price * volume,
                })

        return return_data
