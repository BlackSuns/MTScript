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

        if r.status_code == 200 and r.json()['code'] == 0\
           and r.json()['data']:
            # self.print_log(
            #     'post success: {symbol}/{anchor} on {market}'.format(
            #         symbol=params['symbol'],
            #         anchor=params['anchor'],
            #         market=self.exchange))
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
                    price = data['price']
                    if price and float(price) > 0:
                        (symbol, anchor) = self.part_pair(data['pair'])
                        volume_anchor = data['volume_anchor']
                        volume = data['volume']

                        params = {
                            "symbol": symbol,
                            "market_id": self.exchange_id,
                            "anchor": anchor,
                            "price": price,
                            "volume_24h": volume_anchor,
                            "volume_24h_symbol": volume,
                        }

                        opt_params = ('name', 'percent_change_24h',
                                      'rank', 'market_cap_usd')

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
        except aException as e:
            self.print_log('found error when post: {}'.format(e))

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
