from .base import BaseExchange


class BitfinexExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'bitfinex'
        self.exchange_id = 126
        self.base_url = 'https://api.bitfinex.com/v1'

        self.pair_url = '/symbols'
        self.ticker_url = '/pubticker/'

        self.alias = 'bitfinex'

    # get all available_pairs
    # update result to self.support_pairs
    # self.support_pairs is a list
    def get_available_pair(self):
        url = '{}{}'.format(self.base_url, self.pair_url)
        self.pair_callback(self.get_json_request(url))

    def pair_callback(self, result):
        self.support_pairs = []
        for r in result:
            self.support_pairs.append(r)

    def get_remote_data(self):
        self.get_available_pair()
        result = []

        for pair in self.support_pairs:
            if pair[-3:].upper() in ('USD', 'BTC', 'ETH'):
                url = '{}{}{}'.format(self.base_url, self.ticker_url, pair)
                ticker = self.ticker_callback(self.get_json_request(url))
                ticker['pair'] = '{}/{}'.format(pair[:-3].upper(),
                                                pair[-3:].upper())
                self.print_log('updating {} ... '.format(ticker['pair']))
                result.append(ticker)
        self.print_log(result)
        return result

    def ticker_callback(self, result):
        return {
            'price': result['last_price'],
            'volume_anchor': round(
                float(result['volume']) * float(result['last_price']),
                8),
            'volume': result['volume'],
        }
