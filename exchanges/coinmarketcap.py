from .base import BaseExchange


class CmcExchange(BaseExchange):
    def __init__(self):
        super().__init__()
        self.exchange = 'CoinMarketCap'
        self.exchange_id = 1303
        self.base_url = 'https://api.coinmarketcap.com/v1'

        self.ticker_url = '/ticker/?convert=CNY'

        self.alias = 'CoinMarketCap'
        self.with_name = True

    def get_remote_data(self):
        url = '{}{}'.format(
            self.base_url, self.ticker_url)
        return self.ticker_callback(self.get_json_request(url))

    def ticker_callback(self, result):
        return_data = []

        for i in result:
            # print(i)
            name = i['name']
            symbol = i['symbol']
            if name == 'IOTA' and symbol == 'MIOTA':
                symbol = 'IOT'
            anchor = 'CNY'
            rank = int(i['rank'])
            price = float(i['price_cny']) if i['price_cny'] else 0
            volume_anchor = \
                float(i['24h_volume_cny']) if i['24h_volume_cny'] else 0
            percent_change_24h = \
                float(i['percent_change_24h']) if i['percent_change_24h']\
                else 0
            market_cap_usd = \
                float(i['market_cap_usd']) if i['market_cap_usd']\
                else 0

            if anchor and symbol:
                pair = '{}/{}'.format(symbol.upper(), anchor.upper())
                return_data.append({
                    'name': name,
                    'pair': pair,
                    'price': price,
                    'volume_anchor': volume_anchor,
                    'volume': volume_anchor / price if price else 0,
                    'rank': rank,
                    'percent_change_24h': percent_change_24h,
                    'market_cap_usd': market_cap_usd,
                })

        # print(return_data)
        return return_data
