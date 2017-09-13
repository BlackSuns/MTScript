from .base import BaseExchange


class HitbtcExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'hitbtc'
        self.exchange_id = 79
        self.base_url = 'https://api.hitbtc.com/api/1'

        self.pair_url = '/public/symbols'
        self.ticker_url = '/public/ticker'

        self.alias = 'hitbtc'

    # get all available_pairs
    # update result to self.support_pairs
    # self.support_pairs is a list
    def get_available_pair(self):
        url = '{}{}'.format(self.base_url, self.pair_url)
        self.pair_callback(self.get_json_request(url))

    def pair_callback(self, result):
        self.support_pairs = {}
        for r in result['symbols']:
            self.support_pairs[r['symbol']] = {
                "symbol": r['commodity'],
                "anchor": r['currency'],
            }

    def get_remote_data(self):
        self.get_available_pair()
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []
        for pair in result.keys():
            if pair in self.support_pairs.keys():
                return_data.append({
                    'pair': '{}/{}'.format(
                        self.support_pairs[pair]['symbol'].upper(),
                        self.support_pairs[pair]['anchor'].upper(),
                        ),
                    'price': result[pair]['last'],
                    'volume_anchor': result[pair]['volume_quote'],
                    'volume': result[pair]['volume'],
                })

        # print(return_data)
        return return_data
