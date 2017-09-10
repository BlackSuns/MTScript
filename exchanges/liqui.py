from .base import BaseExchange


class LiquiExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'Liqui'
        self.exchange_id = 46
        self.base_url = 'https://api.liqui.io/api/3'

        self.pair_url = '/info'
        self.ticker_url = '/ticker'

        self.alias = 'Liqui'

    # get all available_pairs
    # update result to self.support_pairs
    # self.support_pairs is a list
    def get_available_pair(self):
        url = '{}{}'.format(self.base_url, self.pair_url)
        self.pair_callback(self.get_json_request(url))

    def pair_callback(self, result):
        self.update_time = result['server_time']
        self.support_pairs = []
        for r in result['pairs'].keys():
            if result['pairs'][r]['hidden'] == 0:
                self.support_pairs.append(r)

    def get_remote_data(self):
        self.get_available_pair()
        query_string = '-'.join(self.support_pairs)
        url = '{}{}/{}?ignore_invalid=1'.format(
            self.base_url, self.ticker_url, query_string)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []
        for i in self.support_pairs:
            pair = str(i).upper().replace('_', '/')

            if i in result.keys():
                return_data.append({
                    'pair': pair,
                    'price': result[i]['last'],
                    'volume_anchor': result[i]['vol'],
                    'volume': result[i]['vol_cur'],
                })

        return return_data
