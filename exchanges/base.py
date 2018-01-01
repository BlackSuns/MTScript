import os
from urllib.parse import urlencode
import json
from configparser import ConfigParser

import arrow
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


class BaseExchange(object):
    ''' This is Base Exchange Object to pull currency data from exchanges
        and record them in database

        Most important func here is update_pairs and update_database

        If you want to add a exchange, inherit this object and do:
        1. create a __init__ func and request a pymysql connection param
        2. do super().__init__(conn, your_exchange_name) in your __init__
           conn is the pymysql connection param metioned above
        3. overload your base_url, ticker_url, and alias if needs, in __init__
        4. overload get_remote_data func, remember to return a list include
           elements like {pair: xx, price: xxx, volume: xxx, volume_anchor: xx}
        5. if a pair use an assigned com_id, override self.assigned_com_id
           with format {pair1: com_id1, pair2_com_id2}
        5. use self.get_json_request to create connection, pass an url
           this function will return you the response if get correct response
        Done and try

        How to use:
        1. create an instance of some exchange object, pass a pymysql conn obj
        2. instance.update_database()
    '''
    CONFIG_PATH = os.path.abspath(
        os.path.dirname(__file__)) + '/../script.conf'
    CONFIG_SECTION = 'cmc_data_db'

    def __init__(self):
        super().__init__()

    def get_remote_data(self):
        ''' get data from markets and return value
            this function should be implemented in extend classes

            return value:
            [
                {
                    pair: 'OMG/ETH',
                    price: 0.03456,
                    volume: 2036,  # volume of symbol
                    volume_cur: 56,  # volume of anchor
                }
                ...
            ]
            e.g.
            pair symbols should be in capital
        '''
        raise NotImplementedError("You should implement this")

    def get_json_request(self, url):
        s = requests.Session()
        s.mount('https://', MyAdapter())
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Content-Type': 'application/json',
        }

        if url.startswith("https://api.etherdelta.com"):
            headers['cookie'] = '__cfduid=d42b240e518dad58587086f22eab9d7f11505272987; _ga=GA1.2.40686394.1505272998; _TRAEFIK_BACKEND=http://10.0.0.13:8001' 

        if url.startswith("https://www.jex.com/"):
            headers['Cookie'] = 'aliyungf_tc=AQAAALsS03qsewEAVURRZWzA5S4Ta4K8; jex_session_id=5a76bf47-5ab5-431e-a60b-fbf387a80b5aFEAJ; Language=zh_CN; _uab_collina=151479147890873463145797; marketSymbol13=11; tradeMarket=1; marketSymbol1=3; chartSettings=%7B%22ver%22%3A3%2C%22charts%22%3A%7B%22chartStyle%22%3A%22CandleStick%22%2C%22mIndic%22%3A%22MA%22%2C%22indics%22%3A%5B%22VOLUME%22%2C%22MACD%22%5D%2C%22indicsStatus%22%3A%22close%22%2C%22period%22%3A%2215m%22%2C%22currentSymbole%22%3A%223%22%2C%22period_weight%22%3A%7B%220%22%3A6%2C%221%22%3A5%2C%222%22%3A8%2C%223%22%3A2%2C%224%22%3A1%2C%227%22%3A0%2C%229%22%3A4%2C%2210%22%3A3%2C%2211%22%3A0%2C%2212%22%3A0%2C%2213%22%3A0%2C%2214%22%3A0%2C%2215%22%3A0%2C%22line%22%3A7%7D%2C%22areaHeight%22%3A%5B%5D%7D%2C%22indics%22%3A%7B%22MA%22%3A%5B7%2C30%2C0%2C0%5D%2C%22EMA%22%3A%5B7%2C30%2C0%2C0%5D%2C%22VOLUME%22%3A%5B5%2C10%5D%2C%22MACD%22%3A%5B12%2C26%2C9%5D%2C%22KDJ%22%3A%5B9%2C3%2C3%5D%2C%22StochRSI%22%3A%5B14%2C14%2C3%2C3%5D%2C%22RSI%22%3A%5B6%2C12%2C24%5D%2C%22DMI%22%3A%5B14%2C6%5D%2C%22OBV%22%3A%5B30%5D%2C%22BOLL%22%3A%5B20%5D%2C%22DMA%22%3A%5B10%2C50%2C10%5D%2C%22TRIX%22%3A%5B12%2C9%5D%2C%22BRAR%22%3A%5B26%5D%2C%22VR%22%3A%5B26%2C6%5D%2C%22EMV%22%3A%5B14%2C9%5D%2C%22WR%22%3A%5B10%2C6%5D%2C%22ROC%22%3A%5B12%2C6%5D%2C%22MTM%22%3A%5B12%2C6%5D%2C%22PSY%22%3A%5B12%2C6%5D%7D%2C%22theme%22%3A%22Dark%22%7D; tradeMarketIndex=1; JSESSIONID=7A0D7E7335DEB9F6CE93C25CC5DBAC62'

        if url.startswith("https://www.bite.ceo") or url.startswith("https://www.cryptopia.co.nz"):
            r = requests.get(url, headers=headers, timeout=30, verify=False)
        else:
            r = requests.get(url, headers=headers, timeout=30)
        # print(r.text)
        # print(url)

        if r.status_code == 200:
            return r.json()
        else:
            self.print_log('someting wrong and return http code: {}'.format(
                r.status_code))

    def post_json_request(self, url, params=None):
        # print(url)
        # print(params)
        r = requests.post(url, data=params)

        # print(r.text)

        if r.status_code == 200:
            return r.json()
        else:
            # print(params)
            error_info = "http code: {}".format(r.status_code)
            if r.status_code == 200:
                try:
                    error_info += ' and server return error: {}'.format(
                        r.json())
                except:
                    pass
            self.print_log(error_info)

    # def post_result(self):
    #     host = 'http://internal.mytoken.io:12306'
    #     endpoint = '/currency/upsertcurrencyonmarket'

    #     request_url = '{host}{endpoint}?source=script'.format(
    #         host=host, endpoint=endpoint)

    #     try:
    #         remote_data = self.get_remote_data()
    #         for data in remote_data:
    #             (symbol, anchor) = self.part_pair(data['pair'])
    #             price = data['price']
    #             volume_anchor = data['volume_anchor']

    #             params = {
    #                 'symbol': symbol,
    #                 'market_id': self.exchange_id,
    #                 'anchor': anchor,
    #                 'price': price,
    #                 'volume_24h': volume_anchor,
    #             }

    #             opt_params = ('name', 'percent_change_24h', 'rank')

    #             for p in opt_params:
    #                 if p in data.keys():
    #                     params[p] = data[p]

    #             self.post_json_request(request_url, params)
    #             # self.print_log(result)
    #     except Exception as e:
    #         self.print_log('found error: {}'.format(e))

    def post_result_batch(self):
        page_size = 2000
        host = self.get_base_url()
        if not host:
            raise RuntimeError('not define base url in config file')

        endpoint = '/currency/batchupsert'

        request_url = '{host}{endpoint}'.format(
            host=host, endpoint=endpoint)
        request_data = []

        try:
            remote_data = self.get_remote_data()
            jobs = self.chunks(remote_data, page_size)
            for j in jobs:
                for data in j:
                    # print(data)

                    (symbol, anchor) = self.part_pair(data['pair'])
                    volume_anchor = data['volume_anchor']
                    volume = data['volume']

                    params = {
                        "symbol": symbol,
                        "market_id": self.exchange_id,
                        "anchor": anchor,
                        "volume_24h": volume_anchor,
                        "volume_24h_symbol": volume,
                    }

                    if 'price' in data.keys():
                        params['price'] = data['price']

                    opt_params = ('name', 'percent_change_24h',
                                  'rank', 'market_cap_usd', 'available_supply',
                                  'total_supply', 'max_supply')

                    for p in opt_params:
                        if p in data.keys():
                            params[p] = data[p]

                    request_data.append(params)

                if not self.with_name:
                    with open(self.exchange_conf, 'r') as f:
                        data = json.load(f)
                    name_symbol = data['name_symbol']
                    for d in request_data:
                        d['name'] = name_symbol.get(d['symbol'], '')

                # print(request_url, {'json': request_data})
                self.post_json_request(
                    request_url, {'json': json.dumps(request_data)})
        except Exception as e:
            self.print_log('found error: {}'.format(e))

    def print_log(self, message, m_type='INFO'):
        m_types = ('INFO', 'WARNING', 'ERROR')
        prefix = '[exchange {}][ {} ]'.format(
            self.exchange, arrow.now().format('YYYY-MM-DD HH:mm:ss:SSS'))
        if str(m_type).upper() in m_types:
            m_type = str(m_type).upper()
        else:
            raise RuntimeError('Invalid log type: {}'.format(m_type))

        print('{} -{}- {}'.format(prefix, m_type, message))

    def get_base_url(self):
        config = ConfigParser()
        config.read(self.CONFIG_PATH)

        if config.has_section('exchange_settings'):
            return config.get('exchange_settings', 'base_url')
        else:
            return None

    def get_config(self):
        args = {
            'host':       'string',
            'port':       'int',
            'user':       'string',
            'password':   'string',
            'db':         'string',
        }
        config = ConfigParser()
        config.read(self.CONFIG_PATH)

        if config.has_section(self.CONFIG_SECTION):
            dictdata = {}
            for arg, argtype in args.items():
                try:
                    if argtype == 'int':
                        dictdata[arg] = config.getint(
                            self.CONFIG_SECTION, arg)
                    elif argtype == 'float':
                        dictdata[arg] = config.getfloat(
                            self.CONFIG_SECTION, arg)
                    elif argtype == 'boolean':
                        dictdata[arg] = config.getboolean(
                            self.CONFIG_SECTION, arg)
                    else:
                        dictdata[arg] = config.get(
                            self.CONFIG_SECTION, arg)
                except:
                    dictdata[arg] = None

            return dictdata
        else:
            return None

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l.
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def part_pair(self, pair):
        ''' part a pair to (symbol, anchor)
        return (None, None) if illegal format
        '''
        result = str(pair).split('/')
        if len(result) == 2:
            return result
        else:
            raise RuntimeError('not valid pair: {}'.format(pair))

    def format_price(self, price):
        if price > 1:
            return round(price, 2)
        else:
            return round(price, 8)
