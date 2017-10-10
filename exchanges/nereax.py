from .base import BaseExchange


class NeraexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'Neraex'
        self.exchange_id = 1334
        self.base_url = 'https://neraex.com/api/v2'

        self.ticker_url = '/tickers'

        self.alias = 'neraex'

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []
        anchors = ('btc', 'jpy')

        for k in result.keys():
            symbol = k[:-3]
            anchor = k[-3:]
            if anchor in anchors:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                price = float(result[k]['ticker']['last']) if result[k]['ticker']['last'] else 0
                volume = float(result[k]['ticker']['vol']) if result[k]['ticker']['vol'] else 0
                return_data.append({
                    'pair': pair,
                    'price': price,
                    'volume_anchor': price * volume,
                    'volume': volume,
                })

        # print(return_data)
        return return_data
